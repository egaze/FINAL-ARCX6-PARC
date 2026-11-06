"""Map-free solution: explore the arena during the run, find the tags, visit them in order.

    ros2 launch explore_solution explore_solution.launch.py

No saved map. SLAM (slam_toolbox, mapping mode) builds the map during the run and
corrects wheel-odometry drift, so positions in "map" are measured from where the
robot started. Nav2 plans on a live obstacle map built from the lidar.

When the referee says RUNNING:
  1. Spin in place at the start, looking for tags.
  2. For each tag in the referee's order:
       - while that tag has not been seen yet, drive to the next point of a sweep
         across the arena and spin there; the camera is on the whole time, and
         every tag seen (any ID) gets its position and facing recorded (median
         of all sightings within `record_range`);
       - as soon as it has been seen, visit it exactly like task_solution's
         tag_visitor: approach region, camera alignment, JPEG TagVisit, 3 s hold.
  3. Tags that failed get a second pass while time is left; then Finish.

The robot never moves before RUNNING (no false start). Everything that talks to
the referee, detects tags (AprilTag 36h11, exact codes, IDs 1/4/7/9) and lines up
with a tag is reused unchanged from task_solution.tag_visitor.TagVisitor.

Sweep points are in metres from the start pose: x forward, y left. The default
pattern covers the PARC arena (7 m x 6 m, start 1 m in front of the back wall,
facing into the arena); set `sweep_points` for another arena.
"""

import math
import threading
import time

import numpy as np
import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped, Twist
from nav2_msgs.action import NavigateToPose
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import LaserScan
import tf2_ros

from task_solution.tag_mapper import detect_tags, quat_to_matrix
from task_solution.tag_visitor import TagVisitor, wrap


# x forward, y left, metres from the start pose (serpentine over the arena)
DEFAULT_SWEEP = [1.0, 0.0,   1.0, -2.2,   2.5, -2.2,   4.0, -2.2,   4.0, 0.0,
                 2.5, 0.0,   2.5, 2.2,    4.0, 2.2,    1.0, 2.2]


class ExploreVisitor(TagVisitor):

    def __init__(self):
        self._ready = False            # TagVisitor starts run() at the end of its __init__
        super().__init__()
        p = lambda n: self.get_parameter(n).value  # noqa: E731
        self.declare_parameter('sweep_points', DEFAULT_SWEEP)
        self.declare_parameter('spin_speed', 0.4)          # rad/s while scanning (slower = more frames per tag)
        self.declare_parameter('record_range', 3.5)        # m: whatever the camera can decode (~3 m); final pose uses the live camera
        self.declare_parameter('min_samples', 3)           # sightings before a tag counts as found
        self.declare_parameter('waypoint_timeout_s', 40.0)
        self.declare_parameter('waypoint_reached', 0.35)   # m
        flat = [float(v) for v in p('sweep_points')]
        self.sweep = list(zip(flat[0::2], flat[1::2]))
        self.next_wp = 0
        self.samples = {}                                  # id -> list of (x, y, facing_yaw)
        self.rec_lock = threading.Lock()
        self.stats = {'frames': 0, 'seen': set(), 'since': time.monotonic()}
        # Spinning in place sweeps a circle of the robot's corner radius (~0.38 m). With the
        # lidar clear beyond spin_clearance all round, the spin cannot hit anything, so it is
        # sent straight to the wheels; the collision monitor would otherwise throttle it to
        # a crawl next to tables and walls (the spins timed out after a few degrees).
        self.declare_parameter('spin_clearance', 0.45)
        self.declare_parameter('direct_cmd_topic', '/cmd_vel')
        self.min_range = None
        self.create_subscription(LaserScan, '/scan_filtered', self.on_scan, qos_profile_sensor_data)
        self.direct_pub = self.create_publisher(Twist, p('direct_cmd_topic'), 10)
        self.get_logger().info(
            f'Explore mode: no map. {len(self.sweep)} sweep points; tags are found during the run.')
        self._ready = True

    # ---------------------------------------------------------------- tag memory
    def load_tags(self, path):
        """No tags.yaml in explore mode: tags are discovered during the run."""
        return {}

    def plausible(self, tag_id, tvec, frame, stamp):
        """No prior positions to cross-check against; the exact 36h11 decode, the ID
        whitelist and the frames-in-a-row rule still apply."""
        return True

    def on_image(self, msg):
        """Own detection step (same detector and frames-in-a-row rule as TagVisitor),
        so every confirmed sighting is also recorded, with progress logging."""
        with self.lock:
            self.last_image = msg
        if self.K is None or not self.detecting or not self._ready:
            return
        if time.monotonic() - self.last_detect < 0.1:      # ~10 Hz
            return
        self.last_detect = time.monotonic()
        gray = self.bridge.imgmsg_to_cv2(msg, 'mono8')
        found = detect_tags(gray, self.K, self.D, self.tag_size)    # 36h11, exact, 1/4/7/9
        stamp = Time.from_msg(msg.header.stamp)
        frame = msg.header.frame_id
        self.stats['frames'] += 1
        for tag_id in found:
            self.stats['seen'].add(tag_id)
        with self.lock:
            for tag_id in list(self.streak):
                if tag_id not in found:
                    self.streak[tag_id] = 0
            confirmed = []
            for tag_id, (tvec, normal) in found.items():
                self.streak[tag_id] = self.streak.get(tag_id, 0) + 1
                if self.streak[tag_id] >= self.min_consecutive:
                    self.detections[tag_id] = (stamp, tvec, normal, frame, msg)
                    confirmed.append((tag_id, tvec, normal))
        rr = float(self.get_parameter('record_range').value)
        for tag_id, tvec, normal in confirmed:
            if float(np.linalg.norm(tvec)) <= rr:
                self.record(tag_id, tvec, normal, frame, stamp)
        if time.monotonic() - self.stats['since'] > 5.0:
            self.get_logger().info(
                f'Camera: {self.stats["frames"]} frames checked in the last 5 s; tag IDs in view: '
                f'{sorted(self.stats["seen"]) or "none"}; known: {sorted(self.tags)}')
            self.stats = {'frames': 0, 'seen': set(), 'since': time.monotonic()}

    def record(self, tag_id, tvec, normal, frame, stamp):
        try:
            tf = self.tf_buffer.lookup_transform(
                self.map_frame, frame, stamp, timeout=Duration(seconds=0.2))
        except tf2_ros.TransformException as e:
            self.get_logger().warn(f'Cannot place tag {tag_id}: {e}', throttle_duration_sec=5.0)
            return
        R = quat_to_matrix(tf.transform.rotation)
        tr = tf.transform.translation
        pos = R @ tvec + np.array([tr.x, tr.y, tr.z])
        n = R @ normal
        with self.rec_lock:
            lst = self.samples.setdefault(tag_id, [])
            lst.append((pos[0], pos[1], math.atan2(n[1], n[0])))
            if len(lst) > 200:
                lst.pop(0)
            a = np.array(lst)
            est = {'x': float(np.median(a[:, 0])), 'y': float(np.median(a[:, 1])),
                   'facing_yaw': math.atan2(float(np.median(np.sin(a[:, 2]))),
                                            float(np.median(np.cos(a[:, 2])))),
                   'samples': len(lst)}
            first = tag_id not in self.tags
            if len(lst) >= int(self.get_parameter('min_samples').value):
                self.tags[tag_id] = est
                if first:
                    self.get_logger().info(
                        f'Found tag {tag_id} at ({est["x"]:.2f}, {est["y"]:.2f}), '
                        f'facing {math.degrees(est["facing_yaw"]):.0f} deg. '
                        f'Known: {sorted(self.tags)}')

    def known(self, tag):
        with self.rec_lock:
            return tag in self.tags

    # ------------------------------------------------------------ exploration
    def spin_scan(self):
        """One full turn in place with the camera on."""
        speed = float(self.get_parameter('spin_speed').value)
        if not self.spin_is_clear():
            self.back_out(0.25)                           # make room before turning
        direct = self.spin_is_clear()
        pub = self.direct_pub if direct else self.cmd_pub
        start = self.pose2d(self.odom_frame)
        if start is None:
            return
        turned, last = 0.0, start[2]
        end = self.now() + Duration(seconds=2 * math.pi / speed + 6.0)
        cmd = Twist()
        cmd.angular.z = speed
        while rclpy.ok() and self.referee.running and self.now() < end and turned < 2 * math.pi:
            if self.target_known():
                break                                      # stop early: next tag found
            if direct and not self.spin_is_clear():        # something came close: be careful
                direct, pub = False, self.cmd_pub
            me = self.pose2d(self.odom_frame)
            if me is not None:
                turned += abs(wrap(me[2] - last))
                last = me[2]
            pub.publish(cmd)
            time.sleep(0.05)
        self.stop()
        self.direct_pub.publish(Twist())
        self.get_logger().info(f'Scan spin: turned {math.degrees(turned):.0f} deg'
                               f'{" (direct, area clear)" if direct else " (through collision monitor)"}.')

    def on_scan(self, msg):
        r = [x for x in msg.ranges if msg.range_min <= x <= msg.range_max]
        self.min_range = min(r) if r else None

    def spin_is_clear(self):
        c = float(self.get_parameter('spin_clearance').value)
        return self.min_range is not None and self.min_range >= c

    def target_known(self):
        t = getattr(self, 'current_target', None)
        return t is not None and self.known(t)

    def goto(self, x, y):
        """Nav2 to a sweep point (any heading). Stops early if the target tag is found
        or the robot stops making progress. Returns when done; never raises."""
        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = self.map_frame
        goal.pose.header.stamp = self.now().to_msg()
        goal.pose.pose.position.x = float(x)
        goal.pose.pose.position.y = float(y)
        goal.pose.pose.orientation.w = 1.0
        fut = self.nav.send_goal_async(goal)
        wall_end = time.monotonic() + 10.0
        while rclpy.ok() and not fut.done():
            if time.monotonic() > wall_end:
                self.cancel_all_nav()
                return
            time.sleep(0.05)
        handle = fut.result()
        if handle is None or not handle.accepted:
            return
        res = handle.get_result_async()
        deadline = self.now() + Duration(
            seconds=float(self.get_parameter('waypoint_timeout_s').value))
        stuck_time = Duration(seconds=float(self.get_parameter('stuck_time_s').value))
        reached = float(self.get_parameter('waypoint_reached').value)
        best, best_at = None, self.now()
        while rclpy.ok() and not res.done():
            me = self.pose2d(self.map_frame)
            d = math.hypot(x - me[0], y - me[1]) if me is not None else None
            stop = (not self.referee.running or self.now() > deadline
                    or self.target_known() or (d is not None and d <= reached))
            if d is not None:
                if best is None or d < best - 0.10:
                    best, best_at = d, self.now()
                elif self.now() - best_at > stuck_time:
                    self.get_logger().warn(f'Sweep point ({x:.1f}, {y:.1f}): no progress; skipping.')
                    stop = True
            if stop:
                handle.cancel_goal_async()
                self.cancel_all_nav()
                return
            time.sleep(0.05)
        if res.result() is not None and res.result().status != GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f'Sweep point ({x:.1f}, {y:.1f}) not reachable; next one.')

    def explore_until_known(self, tag):
        """Drive the sweep (continuing where it left off) until `tag` has been seen."""
        log = self.get_logger()
        self.current_target = tag
        self.set_detecting(True)
        try:
            while (rclpy.ok() and self.referee.running and not self.known(tag)
                   and self.next_wp < len(self.sweep)):
                x, y = self.sweep[self.next_wp]
                self.next_wp += 1
                log.info(f'Looking for tag {tag}: sweep point {self.next_wp}/{len(self.sweep)}'
                         f' ({x:.1f}, {y:.1f}). Known so far: {sorted(self.tags)}')
                self.goto(x, y)
                if not self.known(tag) and self.referee.running:
                    self.spin_scan()
        finally:
            self.current_target = None
        return self.known(tag)

    # -------------------------------------------------------------------- run
    def run(self):
        log = self.get_logger()
        while rclpy.ok() and not getattr(self, '_ready', False):
            time.sleep(0.05)
        while rclpy.ok() and (self.K is None or not self.nav.wait_for_server(timeout_sec=1.0)):
            log.info('Waiting for camera info and Nav2...', throttle_duration_sec=10.0)
            time.sleep(0.5)
        while rclpy.ok():
            while rclpy.ok() and not self.referee.running:
                time.sleep(0.1)
            if not rclpy.ok():
                return
            order = list(self.referee.tag_order)
            log.info(f'Run started. Order {order}. Scanning from the start position.')
            self.current_target = order[0] if order else None
            self.set_detecting(True)
            self.spin_scan()
            for tag in order:
                if not self.referee.running:
                    break
                if tag in self.referee.reported:
                    continue
                if not self.known(tag) and not self.explore_until_known(tag):
                    log.warn(f'Tag {tag}: not found after the whole sweep; skipping it for now.')
                    continue
                self.visit(tag)
                self.set_detecting(True)                   # keep recording tags afterwards
            self.stop()
            for tag in list(self.referee.remaining_tags):  # second pass while time is left
                left = self.referee.time_left_s
                if not self.referee.running or (left is not None and left < 60.0):
                    break
                if not self.known(tag):
                    self.next_wp = 0                       # sweep once more for missing tags
                    if not self.explore_until_known(tag):
                        continue
                log.warn(f'Tag {tag}: retrying.')
                self.visit(tag)
            self.stop()
            if self.referee.running:
                missing = self.referee.remaining_tags
                log.warn(f'Could not report tags {missing}; ending the run.')
                self.referee.finish(completed=False)
            log.info(f'Run done. Tags found: {sorted(self.tags)}')
            while rclpy.ok() and self.referee.running:
                time.sleep(0.1)


def main(args=None):
    rclpy.init(args=args)
    node = ExploreVisitor()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if rclpy.ok():
            node.stop()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
