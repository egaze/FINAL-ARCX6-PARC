"""Visit the AprilTags in the referee's order and report each one.

    ros2 run task_solution tag_visitor --ros-args -p use_sim_time:=true

For each tag in /parc/tag_order (only while the run is RUNNING):
  1. Nav2 drives into an approach REGION in front of the tag (a 0.35 m circle 1.0 m
     out from the tag in maps/tags.yaml, with fallback regions on an arc). It is
     cancelled as soon as the robot is inside, or the tag is confirmed in view.
  2. Fine alignment with the live camera detection: the robot moves until its
     centre (base_footprint) is `standoff` m in front of the tag, on the tag's face
     normal and facing it. Because this step uses what the camera sees, tags.yaml
     only needs to be roughly right.
  3. Once stopped, a fresh camera frame in which the tag is detected is sent as a
     TagVisit on /parc/tag_visit (via RefereeClient), then the robot holds still
     for 3 s.

`standoff` is measured from the robot centre, the same way the arena generator
defines the visit pose (tag position + 0.5 m along its face normal). The top
camera sits about 0.05 m behind the centre, so it ends up about 0.55 m from the tag.
"""

import math
import os
import threading
import time

import numpy as np
import rclpy
import tf2_ros
import yaml
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge
from geometry_msgs.msg import PoseStamped, Twist
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.duration import Duration
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import CameraInfo, Image
from action_msgs.msg import GoalStatus
from action_msgs.srv import CancelGoal

from task_solution.referee import VISIT_HOLD_S, RefereeClient
from task_solution.tag_mapper import detect_tags, quat_to_matrix


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


class TagVisitor(Node):

    def __init__(self):
        super().__init__('tag_visitor')
        default_tags = os.path.join(
            get_package_share_directory('task_solution'), 'maps', 'tags.yaml')
        self.declare_parameter('tags_file', default_tags)
        self.declare_parameter('standoff', 0.5)            # m, robot centre to tag face
        self.declare_parameter('tag_size', 0.12)           # black square edge, m (0.15 m tag incl. white border)
        self.declare_parameter('image_topic', '/camera1/camera1/color/image_raw')
        self.declare_parameter('camera_info_topic', '/camera1/camera1/color/camera_info')
        # Goes through collision_monitor to the wheels, so the final moves stay protected.
        self.declare_parameter('cmd_vel_topic', 'cmd_vel_smoothed')
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_footprint')
        # Nav2 drives to a REGION in front of the tag, not an exact pose: a circle of
        # region_radius around a point approach_distance out from the tag. The arena
        # keeps 1.5 m x 1.2 m in front of every tag clear. Fallback regions sit on an
        # arc around the tag (approach_angles_deg from the tag's face direction).
        self.declare_parameter('approach_distance', 0.75)  # m, region centre to tag
        self.declare_parameter('region_radius', 0.20)      # m: anywhere inside counts as arrived
        self.declare_parameter('approach_angles_deg', [0.0, 25.0, -25.0, 50.0, -50.0])
        self.declare_parameter('nav_timeout_s', 45.0)      # per region
        self.declare_parameter('tag_nav_budget_s', 120.0)  # all regions of one tag together
        self.declare_parameter('back_out_distance', 0.35)  # m reversed after each visit (clear zone)
        self.declare_parameter('stuck_time_s', 8.0)        # no 0.1 m progress for this long = stuck
        self.declare_parameter('handoff_range', 1.0)       # m: tag confirmed this close -> stop Nav2, align
        self.declare_parameter('align_timeout_s', 20.0)
        self.declare_parameter('pos_tolerance', 0.04)      # m (judged distance is 0.5 m; 4 cm is ample)
        self.declare_parameter('yaw_tolerance', 0.06)      # rad (~3.4 deg; the rule allows 12 deg)
        self.declare_parameter('max_linear', 0.25)         # m/s during alignment (robot max 0.5)
        self.declare_parameter('max_angular', 1.0)         # rad/s during alignment (robot max 1.0)
        # Tag cross-checks (on top of the exact AprilTag 36h11 decode in detect_tags):
        self.declare_parameter('min_consecutive', 3)       # frames in a row before a tag is trusted
        self.declare_parameter('max_map_offset', 1.0)      # m: detected tag must be this close to tags.yaml

        p = lambda n: self.get_parameter(n).value  # noqa: E731
        self.standoff = float(p('standoff'))
        self.tag_size = float(p('tag_size'))
        self.map_frame = p('map_frame')
        self.odom_frame = p('odom_frame')
        self.base_frame = p('base_frame')
        self.tags = self.load_tags(os.path.expanduser(p('tags_file')))

        cb = ReentrantCallbackGroup()
        self.bridge = CvBridge()
        self.K = None
        self.D = None
        self.lock = threading.Lock()
        self.last_image = None          # latest sensor_msgs/Image
        self.detections = {}            # id -> (stamp Time, tvec, normal, frame_id)
        self.detecting = False          # only run the detector when it is needed (CPU)
        self.streak = {}                # id -> consecutive frames with a plausible detection
        self.last_detect = 0.0
        self.min_consecutive = int(p('min_consecutive'))
        self.max_map_offset = float(p('max_map_offset'))

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.referee = RefereeClient(self)
        self.nav = ActionClient(self, NavigateToPose, 'navigate_to_pose', callback_group=cb)
        # Cancels every navigate_to_pose goal (zero id + zero stamp), even ones we lost track of.
        self.nav_cancel_all = self.create_client(
            CancelGoal, 'navigate_to_pose/_action/cancel_goal', callback_group=cb)
        self.cmd_pub = self.create_publisher(Twist, p('cmd_vel_topic'), 10)
        self.create_subscription(CameraInfo, p('camera_info_topic'), self.on_info,
                                 qos_profile_sensor_data, callback_group=cb)
        self.create_subscription(Image, p('image_topic'), self.on_image,
                                 qos_profile_sensor_data, callback_group=cb)

        self.get_logger().info(
            f'Loaded tags {sorted(self.tags)}; standoff {self.standoff:.2f} m. '
            'Waiting for the referee to be RUNNING.')
        threading.Thread(target=self.run, daemon=True).start()

    # ------------------------------------------------------------------ setup
    def load_tags(self, path):
        with open(path) as f:
            data = yaml.safe_load(f)
        frame = data.get('frame', 'map')
        if frame != self.map_frame:
            raise RuntimeError(f'{path} is in frame "{frame}", expected "{self.map_frame}"')
        return {int(k): v for k, v in data['tags'].items()}

    def on_info(self, msg):
        if self.K is None:
            self.K = np.array(msg.k, dtype=np.float64).reshape(3, 3)
            self.D = np.array(msg.d, dtype=np.float64)

    def on_image(self, msg):
        with self.lock:
            self.last_image = msg
        if self.K is None or not self.detecting:
            return
        if time.monotonic() - self.last_detect < 0.1:     # ~10 Hz is plenty, saves CPU
            return
        self.last_detect = time.monotonic()
        gray = self.bridge.imgmsg_to_cv2(msg, 'mono8')
        found = detect_tags(gray, self.K, self.D, self.tag_size)   # 36h11, exact, IDs 1/4/7/9
        stamp = Time.from_msg(msg.header.stamp)
        confirmed = {}
        for tag_id, (tvec, normal) in found.items():
            if not self.plausible(tag_id, tvec, msg.header.frame_id, stamp):
                continue
            confirmed[tag_id] = (tvec, normal)
        with self.lock:
            for tag_id in list(self.streak):
                if tag_id not in confirmed:
                    self.streak[tag_id] = 0
            for tag_id, (tvec, normal) in confirmed.items():
                self.streak[tag_id] = self.streak.get(tag_id, 0) + 1
                if self.streak[tag_id] == self.min_consecutive:
                    self.get_logger().info(
                        f'Tag {tag_id} recognised (AprilTag 36h11, {self.min_consecutive} frames in a row,'
                        f' {float(np.linalg.norm(tvec)):.2f} m from the camera).',
                        throttle_duration_sec=3.0)
                if self.streak[tag_id] >= self.min_consecutive:
                    self.detections[tag_id] = (stamp, tvec, normal, msg.header.frame_id, msg)

    def plausible(self, tag_id, tvec, frame, stamp):
        """Cross-check a detection against tags.yaml: the tag with this ID must be
        within max_map_offset of where the mapping run recorded it. Rejects a
        misread ID or a different tag that happens to be in view."""
        if tag_id not in self.tags:
            return False
        try:
            tf = self.tf_buffer.lookup_transform(
                self.map_frame, frame, stamp, timeout=Duration(seconds=0.05))
        except tf2_ros.TransformException:
            return True     # cannot check (no map pose yet); the streak still applies
        R = quat_to_matrix(tf.transform.rotation)
        tr = tf.transform.translation
        pos = R @ tvec + np.array([tr.x, tr.y, tr.z])
        t = self.tags[tag_id]
        off = math.hypot(pos[0] - t['x'], pos[1] - t['y'])
        if off > self.max_map_offset:
            self.get_logger().warn(
                f'Rejected tag {tag_id}: seen {off:.2f} m from its tags.yaml position '
                f'(limit {self.max_map_offset:.2f} m).', throttle_duration_sec=2.0)
            return False
        return True

    # ---------------------------------------------------------------- helpers
    def now(self):
        return self.get_clock().now()

    def sleep(self, seconds):
        """Sleep in node time (sim time when use_sim_time is set)."""
        end = self.now() + Duration(seconds=seconds)
        while rclpy.ok() and self.now() < end:
            time.sleep(0.02)

    def stop(self):
        self.cmd_pub.publish(Twist())

    def pose2d(self, frame):
        """(x, y, yaw) of the robot base in `frame`, or None."""
        try:
            tf = self.tf_buffer.lookup_transform(frame, self.base_frame, Time())
        except tf2_ros.TransformException:
            return None
        t = tf.transform.translation
        return t.x, t.y, yaw_of(tf.transform.rotation)

    def approach_region(self, tag, angle_deg):
        """Centre (x, y) and facing yaw of an approach region for the tag, in the map
        frame: approach_distance from the tag, angle_deg off its face direction."""
        t = self.tags[tag]
        a = float(t['facing_yaw']) + math.radians(angle_deg)
        d = float(self.get_parameter('approach_distance').value)
        return t['x'] + d * math.cos(a), t['y'] + d * math.sin(a), wrap(a + math.pi)

    def live_target(self, tag, max_age=0.5):
        """Standoff pose (x, y, yaw) in the odom frame from a recent camera detection,
        plus the camera-to-tag range. None if the tag was not seen recently."""
        with self.lock:
            det = self.detections.get(tag)
        if det is None:
            return None
        stamp, tvec, normal, frame = det[:4]
        if (self.now() - stamp) > Duration(seconds=max_age):
            return None
        try:
            tf = self.tf_buffer.lookup_transform(
                self.odom_frame, frame, stamp, timeout=Duration(seconds=0.1))
        except tf2_ros.TransformException:
            return None
        R = quat_to_matrix(tf.transform.rotation)
        tr = tf.transform.translation
        pos = R @ tvec + np.array([tr.x, tr.y, tr.z])
        n = R @ normal
        face = math.atan2(n[1], n[0])
        yaw = wrap(face + math.pi)
        x = pos[0] + self.standoff * math.cos(face)
        y = pos[1] + self.standoff * math.sin(face)
        return (x, y, yaw), float(np.linalg.norm(tvec))

    # ------------------------------------------------------------- navigation
    def cancel_all_nav(self):
        """Cancel every Nav2 navigate_to_pose goal and stop the wheels."""
        if self.nav_cancel_all.service_is_ready():
            self.nav_cancel_all.call_async(CancelGoal.Request())   # zero id/stamp = all goals
        self.stop()

    def back_out(self, distance, speed=0.2):
        """Reverse straight back `distance` m (odometry), e.g. away from a tag just
        visited: the area in front of every tag is kept clear, and Nav2 cannot plan
        from right next to the tag post."""
        start = self.pose2d(self.odom_frame)
        if start is None or distance <= 0.0:
            return
        end = self.now() + Duration(seconds=distance / speed + 3.0)
        cmd = Twist()
        cmd.linear.x = -speed
        while rclpy.ok() and self.referee.running and self.now() < end:
            me = self.pose2d(self.odom_frame)
            if me is not None and math.hypot(me[0] - start[0], me[1] - start[1]) >= distance:
                break
            self.cmd_pub.publish(cmd)
            time.sleep(0.05)
        self.stop()

    def navigate(self, x, y, yaw, tag, radius, timeout):
        """Drive with Nav2 into the region of `radius` around (x, y). Returns
        'in_region' (Nav2 cancelled as soon as the robot centre is inside; heading
        does not matter, the camera alignment turns the robot), 'arrived' (Nav2
        finished), 'tag_in_view' (target tag confirmed within handoff_range: Nav2
        cancelled, camera takes over) or 'failed'. Every wait has a wall-clock limit so a lost Nav2 reply cannot
        block the run."""
        log = self.get_logger()
        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = self.map_frame
        goal.pose.header.stamp = self.now().to_msg()
        goal.pose.pose.position.x = float(x)
        goal.pose.pose.position.y = float(y)
        goal.pose.pose.orientation.z = math.sin(yaw / 2)
        goal.pose.pose.orientation.w = math.cos(yaw / 2)

        fut = self.nav.send_goal_async(goal)
        wall_end = time.monotonic() + 10.0
        while rclpy.ok() and not fut.done():
            if time.monotonic() > wall_end:
                log.warn(f'Tag {tag}: Nav2 did not answer the goal within 10 s; cancelling.')
                self.cancel_all_nav()
                return 'failed'
            time.sleep(0.05)
        handle = fut.result()
        if handle is None or not handle.accepted:
            log.warn(f'Tag {tag}: Nav2 rejected the goal.')
            return 'failed'
        res = handle.get_result_async()
        handoff = float(self.get_parameter('handoff_range').value)
        deadline = self.now() + Duration(seconds=timeout)
        wall_end = time.monotonic() + 3 * timeout       # in case the sim clock stalls
        next_log = time.monotonic()
        stuck_time = Duration(seconds=float(self.get_parameter('stuck_time_s').value))
        best, best_at = None, self.now()
        while rclpy.ok() and not res.done():
            me = self.pose2d(self.map_frame)
            if me is not None:
                d = math.hypot(x - me[0], y - me[1])
                if best is None or d < best - 0.10:
                    best, best_at = d, self.now()
                elif self.now() - best_at > stuck_time:
                    handle.cancel_goal_async()
                    self.cancel_all_nav()
                    log.warn(f'Tag {tag}: no progress for {stuck_time.nanoseconds * 1e-9:.0f} s;'
                             ' backing up and retrying.')
                    return 'stuck'
            if me is not None and math.hypot(x - me[0], y - me[1]) <= radius:
                handle.cancel_goal_async()
                self.cancel_all_nav()
                log.info(f'Tag {tag}: inside the approach region; aligning with the camera.')
                return 'in_region'
            live = self.live_target(tag)
            if live is not None and live[1] <= handoff:
                handle.cancel_goal_async()
                self.cancel_all_nav()
                log.info(f'Tag {tag}: in view at {live[1]:.2f} m; stopping Nav2, aligning with the camera.')
                return 'tag_in_view'
            if not self.referee.running or self.now() > deadline or time.monotonic() > wall_end:
                handle.cancel_goal_async()
                self.cancel_all_nav()
                log.warn(f'Tag {tag}: navigation cancelled '
                         f'({"run not RUNNING" if not self.referee.running else "timeout"}).')
                return 'failed'
            if time.monotonic() >= next_log:
                dist = f'{math.hypot(x - me[0], y - me[1]):.2f} m to go' if me else 'no map pose'
                log.info(f'Tag {tag}: navigating, {dist}; tag '
                         f'{"seen at %.2f m" % live[1] if live else "not in view"}.')
                next_log = time.monotonic() + 5.0
            time.sleep(0.05)
        ok = res.result() is not None and res.result().status == GoalStatus.STATUS_SUCCEEDED
        if not ok:
            log.warn(f'Tag {tag}: Nav2 did not reach the visit pose.')
        return 'arrived' if ok else 'failed'

    def align(self, tag):
        """Move until the robot centre is `standoff` m from the tag, square to its face."""
        max_v = float(self.get_parameter('max_linear').value)
        max_w = float(self.get_parameter('max_angular').value)
        pos_tol = float(self.get_parameter('pos_tolerance').value)
        yaw_tol = float(self.get_parameter('yaw_tolerance').value)
        deadline = self.now() + Duration(
            seconds=float(self.get_parameter('align_timeout_s').value))
        target = None          # (x, y, yaw) in odom, refreshed whenever the tag is seen
        search_dir = 1.0
        rate = 0.05
        in_place = False       # position reached: only re-drive if it drifts 2x the tolerance

        while rclpy.ok() and self.referee.running:
            if self.now() > deadline:
                self.stop()
                self.get_logger().warn(f'Tag {tag}: alignment timed out.')
                return target is not None
            live = self.live_target(tag)
            if live is not None:
                target = live[0]
            me = self.pose2d(self.odom_frame)
            if me is None:
                time.sleep(rate)
                continue

            if target is None:
                # Not seen yet: turn towards where tags.yaml says it is, then search.
                cmd = Twist()
                mp = self.pose2d(self.map_frame)
                if mp is not None:
                    t = self.tags[tag]
                    err = wrap(math.atan2(t['y'] - mp[1], t['x'] - mp[0]) - mp[2])
                    search_dir = 1.0 if err >= 0 else -1.0
                    cmd.angular.z = search_dir * min(max_w, max(0.15, abs(err)))
                else:
                    cmd.angular.z = search_dir * 0.3
                self.cmd_pub.publish(cmd)
                time.sleep(rate)
                continue

            tx, ty, tyaw = target
            dx, dy = tx - me[0], ty - me[1]
            dist = math.hypot(dx, dy)
            cmd = Twist()
            if dist <= pos_tol:
                in_place = True
            elif dist > 2 * pos_tol:
                in_place = False
            if not in_place:
                heading = math.atan2(dy, dx)
                err = wrap(heading - me[2])
                direction = 1.0
                if abs(err) > math.pi / 2:          # target is behind: reverse to it
                    err = wrap(err - math.pi)
                    direction = -1.0
                cmd.angular.z = max(-max_w, min(max_w, 2.5 * err))
                # Drive while turning: full speed when pointing at the target, fading
                # to zero at ~35 deg off, instead of stopping to turn first.
                if abs(err) < 0.6:
                    v = min(max_v, 1.2 * dist + 0.03) * max(0.0, math.cos(err * 2.6))
                    cmd.linear.x = direction * v
            else:
                err = wrap(tyaw - me[2])
                if abs(err) <= yaw_tol:
                    self.stop()
                    return True
                cmd.angular.z = max(-max_w, min(max_w, 2.5 * err))
                if abs(cmd.angular.z) < 0.15:     # below this the wheels barely turn it
                    cmd.angular.z = math.copysign(0.15, err)
            self.cmd_pub.publish(cmd)
            time.sleep(rate)
        self.stop()
        return False

    # ----------------------------------------------------------------- report
    def capture(self, tag, timeout=3.0):
        """A camera frame taken after the robot stopped in which the tag is detected
        (and passed the 36h11 / ID / consecutive-frame / tags.yaml checks)."""
        after = self.now()
        end = after + Duration(seconds=timeout)
        while rclpy.ok() and self.now() < end:
            with self.lock:
                det = self.detections.get(tag)
            # det[4] is the exact frame the tag was confirmed in; it must be newer than the stop.
            if det is not None and det[0] > after:
                img, tvec, normal = det[4], det[1], det[2]
                # Angle between the tag's face normal and the camera's view axis
                # (optical z): 0 deg means the camera looks straight at the face.
                off = math.degrees(math.acos(max(-1.0, min(1.0, -float(normal[2])))))
                return img, (float(np.linalg.norm(tvec)), off)
            time.sleep(0.03)
        return None, None

    def visit(self, tag):
        log = self.get_logger()
        if tag not in self.tags:
            log.error(f'Tag {tag} is not in tags.yaml; skipping it.')
            return False
        angles = [float(a) for a in self.get_parameter('approach_angles_deg').value]
        radius = float(self.get_parameter('region_radius').value)
        per_region = float(self.get_parameter('nav_timeout_s').value)
        budget_end = time.monotonic() + float(self.get_parameter('tag_nav_budget_s').value)
        with self.lock:
            self.streak.clear()
            self.detections.pop(tag, None)
        self.detecting = True           # look for the tag while driving, to hand off early
        for i, angle in enumerate(angles):
            left = budget_end - time.monotonic()
            if left <= 5.0:
                log.warn(f'Tag {tag}: navigation budget used up; aligning from here.')
                break
            x, y, yaw = self.approach_region(tag, angle)
            log.info(f'Tag {tag}: driving to the approach region around ({x:.2f}, {y:.2f}),'
                     f' radius {radius:.2f} m, {angle:+.0f} deg off the tag face'
                     f' [region {i + 1}/{len(angles)}]')
            outcome = self.navigate(x, y, yaw, tag, radius, min(per_region, left))
            if outcome == 'stuck':
                self.back_out(float(self.get_parameter('back_out_distance').value))
                left = budget_end - time.monotonic()
                if left > 5.0:
                    outcome = self.navigate(x, y, yaw, tag, radius, min(per_region, left))
            if outcome not in ('failed', 'stuck'):
                break
            if not self.referee.running:
                self.detecting = False
                return False
        self.cancel_all_nav()           # Nav2 must not drive while the camera alignment does
        # Even if Nav2 did not report success, try the camera alignment from here.
        self.detecting = True
        try:
            if not self.align(tag):
                log.warn(f'Tag {tag}: could not align precisely; reporting from here if visible.')
            self.stop()
            self.sleep(0.3)                   # let the robot settle before the photo
            img, info = self.capture(tag)
        finally:
            self.detecting = False
        if img is None:
            log.error(f'Tag {tag}: not visible in the camera; not reporting it.')
            return False
        log.info(f'Tag {tag}: camera-to-tag range {info[0]:.3f} m, '
                 f'{info[1]:.1f} deg off square-on.')
        if self.referee.report_tag(tag, img):
            self.sleep(VISIT_HOLD_S + 0.1)    # hold still as the rules require
            # Leave the tag post before planning to the next tag (Nav2 cannot plan from here).
            self.back_out(float(self.get_parameter('back_out_distance').value))
            return True
        return False

    def run(self):
        log = self.get_logger()
        while rclpy.ok() and (self.K is None or not self.nav.wait_for_server(timeout_sec=1.0)):
            log.info('Waiting for camera info and Nav2...', throttle_duration_sec=10.0)
            time.sleep(0.5)
        while rclpy.ok():
            while rclpy.ok() and not self.referee.running:
                time.sleep(0.1)
            if not rclpy.ok():
                return
            order = list(self.referee.tag_order)
            log.info(f'Run started. Visiting tags in order {order}.')
            for tag in order:
                if not self.referee.running:
                    break
                if tag in self.referee.reported:
                    continue
                self.visit(tag)
            self.stop()
            if self.referee.running:
                missing = self.referee.remaining_tags
                log.warn(f'Could not report tags {missing}; ending the run.')
                self.referee.finish(completed=False)
            log.info('Run done.')
            while rclpy.ok() and self.referee.running:
                time.sleep(0.1)


def main(args=None):
    rclpy.init(args=args)
    node = TagVisitor()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
