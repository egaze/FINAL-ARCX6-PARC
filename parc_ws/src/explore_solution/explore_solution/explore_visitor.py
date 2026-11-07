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
from geometry_msgs.msg import PoseStamped, Twist, TwistStamped
from nav2_msgs.action import NavigateToPose
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import Image, LaserScan, PointCloud2
import tf2_ros

import cv2
from apriltag_msgs.msg import AprilTagDetectionArray

from task_solution.tag_mapper import DICT, PARAMS, detect_tags, quat_to_matrix
from task_solution.tag_visitor import TagVisitor, wrap


# x forward, y left, metres from the start pose (serpentine over the arena)
DEFAULT_SWEEP = [1.0, 0.0,   1.0, -2.2,   2.5, -2.2,   4.0, -2.2,   4.0, 0.0,
                 2.5, 0.0,   2.5, 2.2,    4.0, 2.2,    1.0, 2.2]


class SafeCmd:
    """The visitor's own velocity output (replaces TagVisitor's Twist publisher).

    * Publishes on cmd_vel_topic (cmd_vel_smoothed = the collision monitor's input), never
      to the wheels directly: the collision monitor stays the final safety layer.
    * Twist or TwistStamped (stamped_cmd_vel), matching the Nav2 chain in this mode; stamped
      messages carry the current time and the robot base frame.
    * Yields to Nav2: while Nav2 commands (cmd_vel_nav, controller and recovery behaviours)
      or its velocity smoother may still be winding down, our commands are not sent, so the
      collision monitor never receives two interleaved command streams.
    """

    def __init__(self, node):
        self.node = node
        g = lambda n: node.get_parameter(n).value  # noqa: E731
        self.stamped = bool(g('stamped_cmd_vel'))
        self.frame = g('base_frame')
        self.quiet = float(g('nav_quiet_s'))
        self.last_nav = 0.0
        self.yielded = 0
        msg_type = TwistStamped if self.stamped else Twist
        node.destroy_publisher(node.cmd_pub)               # TagVisitor's Twist publisher
        self.pub = node.create_publisher(msg_type, g('cmd_vel_topic'), 10)
        node.create_subscription(msg_type, g('nav_cmd_topic'), self.on_nav_cmd, 10)
        node.get_logger().info(
            f'Own velocity commands: {g("cmd_vel_topic")} ({msg_type.__name__}, via the collision '
            f'monitor); yielding to Nav2 while {g("nav_cmd_topic")} is active.')

    def on_nav_cmd(self, _msg):
        self.last_nav = time.monotonic()

    def nav_active(self):
        return time.monotonic() - self.last_nav < self.quiet

    def publish(self, twist):
        if self.nav_active():
            self.yielded += 1
            if self.yielded == 1 or self.yielded % 40 == 0:
                self.node.get_logger().info('Nav2 is still commanding: own move waits.')
            return
        self.yielded = 0
        if self.stamped:
            out = TwistStamped()
            out.header.stamp = self.node.get_clock().now().to_msg()
            out.header.frame_id = self.frame
            out.twist = twist
            self.pub.publish(out)
        else:
            self.pub.publish(twist)


class ExploreVisitor(TagVisitor):

    def __init__(self):
        self._ready = False            # TagVisitor starts run() at the end of its __init__
        super().__init__()
        p = lambda n: self.get_parameter(n).value  # noqa: E731
        self.declare_parameter('sweep_points', DEFAULT_SWEEP)
        self.declare_parameter('spin_speed', 0.4)          # rad/s while scanning (slower = more frames per tag)
        self.declare_parameter('record_range', 10.0)       # m: any tag the camera can read; re-measured from close up
        self.declare_parameter('min_samples', 2)           # recorded sightings before a tag counts as found
        self.declare_parameter('waypoint_timeout_s', 40.0)
        self.declare_parameter('waypoint_reached', 0.35)   # m
        # "Good enough by the rules" during the final line-up: report at once instead of
        # turning to hit a tighter internal target (rule: 0.5 m, facing within 12 deg)
        self.declare_parameter('accept_cam_range', [0.49, 0.61])   # camera->tag along the normal
        self.declare_parameter('accept_angle_deg', 8.0)
        self.declare_parameter('accept_lateral', 0.08)            # m off the tag's normal line
        # Arena bounds [xmin, xmax, ymin, ymax] in the map frame (set by the launch file in
        # arena mode; empty = unknown). Tag estimates outside are pulled onto the wall.
        self.declare_parameter('arena_bounds', [0.0])
        self.declare_parameter('drive_stuck_s', 8.0)       # s without moving 0.1 m (or turning) = stuck
        # task_solution's visit drive counts 'not getting closer' as stuck; give detours more time
        self.set_parameters([rclpy.parameter.Parameter('stuck_time_s', value=10.0)])
        flat = [float(v) for v in p('sweep_points')]
        self.sweep = list(zip(flat[0::2], flat[1::2]))
        self.next_wp = 0
        self.samples = {}                                  # id -> list of (x, y, facing_yaw)
        self.rec_lock = threading.Lock()
        self.stats = {'frames': 0, 'seen': {}, 'since': time.monotonic()}
        self.hits = {}                                     # id -> recent detection times
        self.declare_parameter('confirm_hits', 2)
        self.hints = {}                                    # id -> (x, y, range) from ANY decode
        self.cands = []                                    # unread tag-like squares: dicts x,y,n,done
        self.declare_parameter('candidate_min_hits', 5)
        # Go and measure EVERY tag seen (not reported, just approached), so all positions
        # are measured from close up and later tags need no search.
        self.declare_parameter('measure_all_tags', True)
        self.declare_parameter('measure_distance', 1.6)   # m: a tag counts as measured when seen this close
        self.measure_tries = {}
        self.declare_parameter('max_candidates_per_tag', 0)   # tag-like squares: off (mostly false)
        self.declare_parameter('confirm_distance', 1.3)   # m: re-measure far-seen tags from here
        self.declare_parameter('camera_lag_s', 0.5)       # frames may be stamped this much before 'now'
        self.declare_parameter('confirm_window_s', 2.0)
        # Spinning in place sweeps a circle of the robot's corner radius (~0.38 m). Without
        # lidar clearance beyond spin_clearance all round, the robot first backs out a little.
        # The spin itself goes through the collision monitor like every other command.
        self.declare_parameter('spin_clearance', 0.75)   # lidar sees table BASES only: tabletops overhang ~0.2 m
        self.min_range = None
        self.create_subscription(LaserScan, '/scan_filtered', self.on_scan, qos_profile_sensor_data)
        # Depth fusion: OpenCV reads the tag (ID + centre pixel) in the colour image; for tags
        # farther than depth_min_range the DISTANCE comes from the depth image at that pixel
        # (sim noise ~4 cm at 3 m) instead of the tag's pixel size (~1 m wrong at 3 m).
        # Tag detector: 'apriltag' = apriltag_ros (official AprilTag library; in the sim it read
        # 351 tag sightings where OpenCV read 10 on the same frames) via its TF frames tag_N;
        # 'opencv' = cv2.aruco on the colour image.
        self.declare_parameter('detector', 'apriltag')
        self.declare_parameter('detections_topic', '/camera1/camera1/color/detections')
        self.declare_parameter('tag_frame_prefix', 'tag_')
        self.img_buf = {}                                  # stamp ns -> colour image msg
        self.create_subscription(AprilTagDetectionArray, p('detections_topic'), self.on_apriltag, 10)
        self.declare_parameter('use_depth', True)
        self.declare_parameter('depth_topic', '/camera1/camera1/depth/image_rect_raw')
        self.declare_parameter('depth_min_range', 1.0)
        self.last_depth = None
        self.depth_used = 0
        self.create_subscription(Image, p('depth_topic'), lambda m: setattr(self, 'last_depth', m),
                                 qos_profile_sensor_data)
        # Own velocity commands (alignment, scan spins, back-outs) -> cmd_vel_smoothed, the
        # collision monitor's input, so the collision monitor is always the last step before
        # the wheels. Same message type as the Nav2 chain: TwistStamped on the robot
        # (stamped_cmd_vel, set by robot:=true), Twist in the sim.
        self.declare_parameter('stamped_cmd_vel', False)
        # Arbitration: the velocity smoother also publishes on cmd_vel_smoothed, for up to its
        # velocity_timeout (1.0 s in nav2_params_*.yaml) after Nav2's last command. Our moves
        # yield until Nav2's command topic (cmd_vel_nav) has been silent for nav_quiet_s.
        self.declare_parameter('nav_cmd_topic', 'cmd_vel_nav')
        self.declare_parameter('nav_quiet_s', 1.1)
        # Fixed moves at the start of the run, before the first scan (e.g. out of the start
        # corner): "forward 1.3, left 90, forward 1.0" (m / deg; also back, right). Empty = off.
        # Driven through the collision monitor; a blocked move ends the opening early.
        self.declare_parameter('opening', '')
        self.declare_parameter('visit_attempts', 2)      # tries per tag before moving on
        # Reversing (after a photo, a failed line-up, when stuck, before a scan spin): slow,
        # ramped, and limited by the free space behind (lidar) minus a margin for tabletops
        self.declare_parameter('back_out_speed', 0.12)       # m/s (task_solution used 0.3)
        self.declare_parameter('back_out_margin', 0.25)      # m kept free behind the robot
        self.declare_parameter('rear_edge', 0.30)            # m, base centre to back edge
        self.declare_parameter('half_width', 0.23)           # m
        # Reverse ONLY when the depth cameras see something (e.g. a tabletop) too close in
        # front: while Nav2 drives, an obstacle within front_close of the front edge for
        # front_close_s cancels the goal and the robot backs off front_backoff m.
        self.declare_parameter('front_close', 0.15)          # m beyond the front edge
        self.declare_parameter('front_close_s', 0.5)         # s it must stay that close
        self.declare_parameter('front_backoff', 0.15)        # m reversed
        self.declare_parameter('front_clouds', ['/depth_obstacles/camera1', '/depth_obstacles/camera2'])
        self.front_seen = {}                                 # cloud topic -> (time, close?)
        self.front_since = None
        self.front_cooldown = 0.0
        self.pending_backoff = False
        for topic in p('front_clouds'):
            self.create_subscription(PointCloud2, topic, lambda m, t=topic: self.on_front_cloud(t, m),
                                     qos_profile_sensor_data)
        self.create_timer(0.1, self.front_watchdog)
        self.cmd_pub = SafeCmd(self)
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
        """Own detection step (same exact 36h11 detector as TagVisitor). A tag counts once
        it is decoded in `confirm_hits` frames within `confirm_window_s` (not necessarily
        in a row: near the ~3 m range limit it decodes in only some frames). Every
        confirmed sighting is recorded, with progress logging."""
        with self.lock:
            self.last_image = msg
            ns = Time.from_msg(msg.header.stamp).nanoseconds
            self.img_buf[ns] = msg
            for k in sorted(self.img_buf)[:-40]:
                del self.img_buf[k]
        if self.K is None or not self.detecting or not self._ready:
            return
        if self.get_parameter('detector').value != 'opencv':
            return                                          # apriltag_ros path: on_apriltag()
        if time.monotonic() - self.last_detect < 0.1:      # ~10 Hz
            return
        self.last_detect = time.monotonic()
        gray = self.bridge.imgmsg_to_cv2(msg, 'mono8')
        found = detect_tags(gray, self.K, self.D, self.tag_size)    # 36h11, exact, 1/4/7/9
        self.process(found, msg, gray)

    def on_apriltag(self, arr):
        """apriltag_ros detections -> same (tvec, normal) format as detect_tags, using the
        tag_N TF frames apriltag_ros publishes (camera frame -> tag, at the image time)."""
        if (self.K is None or not self.detecting or not getattr(self, '_ready', False)
                or self.get_parameter('detector').value == 'opencv' or not arr.detections):
            return
        stamp = Time.from_msg(arr.header.stamp)
        with self.lock:
            img = self.img_buf.get(stamp.nanoseconds)
            if img is None and self.img_buf:               # nearest frame within 0.2 s
                k = min(self.img_buf, key=lambda t: abs(t - stamp.nanoseconds))
                img = self.img_buf[k] if abs(k - stamp.nanoseconds) < 2e8 else None
        if img is None:
            return
        frame = img.header.frame_id
        prefix = self.get_parameter('tag_frame_prefix').value
        found = {}
        for d in arr.detections:
            if d.id not in (1, 4, 7, 9) or d.hamming != 0:
                continue
            try:
                tf = self.tf_buffer.lookup_transform(frame, f'{prefix}{d.id}', stamp,
                                                     timeout=Duration(seconds=0.05))
            except tf2_ros.TransformException:
                continue
            t = tf.transform.translation
            tvec = np.array([t.x, t.y, t.z])
            normal = quat_to_matrix(tf.transform.rotation)[:, 2]
            if float(normal @ tvec) > 0:                    # make it point out of the face, at us
                normal = -normal
            found[int(d.id)] = (tvec, normal)
        if found:
            self.process(found, img, None)

    def process(self, found, msg, gray):
        """Shared by both detectors: depth range, confirmation, memory, hints, stats."""
        if found and bool(self.get_parameter('use_depth').value):
            found = self.depth_correct(found, msg)
        stamp = Time.from_msg(msg.header.stamp)
        frame = msg.header.frame_id
        self.stats['frames'] += 1
        now = time.monotonic()
        win = float(self.get_parameter('confirm_window_s').value)
        need = int(self.get_parameter('confirm_hits').value)
        for tag_id, (tvec, _) in found.items():
            d = float(np.linalg.norm(tvec))
            c, dmin = self.stats['seen'].get(tag_id, (0, 99.0))
            self.stats['seen'][tag_id] = (c + 1, min(dmin, d))
        with self.lock:
            confirmed = []
            for tag_id, (tvec, normal) in found.items():
                hits = [t for t in self.hits.get(tag_id, []) if now - t <= win] + [now]
                self.hits[tag_id] = hits
                if len(hits) >= need:
                    self.detections[tag_id] = (stamp, tvec, normal, frame, msg)
                    confirmed.append((tag_id, tvec, normal))
        self.update_hints(gray, found, frame, stamp)
        rr = float(self.get_parameter('record_range').value)
        for tag_id, tvec, normal in confirmed:
            if float(np.linalg.norm(tvec)) <= rr:
                self.record(tag_id, tvec, normal, frame, stamp)
        if time.monotonic() - self.stats['since'] > 5.0:
            seen = ', '.join(f'{i}: {c}x, closest {d:.1f} m'
                             for i, (c, d) in sorted(self.stats['seen'].items())) or 'none'
            self.get_logger().info(
                f'Camera: {self.stats["frames"]} frames checked in the last 5 s; '
                f'tags decoded: {seen}; known: {sorted(self.tags)}; depth-measured: {self.depth_used}')
            self.depth_used = 0
            self.stats = {'frames': 0, 'seen': {}, 'since': time.monotonic()}

    def depth_correct(self, found, img):
        """Replace the size-based range of far tags with the depth camera's measurement at
        the tag's centre pixel (same lens/resolution, 1.5 cm apart). Keeps OpenCV's estimate
        when depth is missing, stale or inconsistent."""
        d = self.last_depth
        if d is None or d.encoding not in ('16UC1', 'mono16'):
            return found
        dt = abs((Time.from_msg(d.header.stamp) - Time.from_msg(img.header.stamp)).nanoseconds) * 1e-9
        if dt > 0.4:                  # depth arrives ~0.2-0.35 s after colour (sim converter)
            return found
        depth = np.frombuffer(bytes(d.data), dtype=np.uint16).reshape(d.height, d.width)
        sx, sy = d.width / float(img.width), d.height / float(img.height)
        out = {}
        for tag_id, (tvec, normal) in found.items():
            tvec = np.asarray(tvec, dtype=float)
            if np.linalg.norm(tvec) < float(self.get_parameter('depth_min_range').value) or tvec[2] <= 0:
                out[tag_id] = (tvec, normal)
                continue
            u = self.K[0, 0] * tvec[0] / tvec[2] + self.K[0, 2]
            v = self.K[1, 1] * tvec[1] / tvec[2] + self.K[1, 2]
            cu, cv_ = int(round(u * sx)), int(round(v * sy))
            win = depth[max(cv_ - 3, 0):cv_ + 4, max(cu - 3, 0):cu + 4].astype(float) * 0.001
            win = win[(win > 0.3) & (win < 8.0)]
            if win.size >= 10 and np.std(win) < 0.08:       # flat panel: consistent readings
                z = float(np.median(win))
                out[tag_id] = (tvec * (z / tvec[2]), normal)  # same ray, measured depth
                self.depth_used += 1
            else:
                out[tag_id] = (tvec, normal)
        return out

    def update_hints(self, gray, found, frame, stamp):
        """Clues for the search, used before the slow sweep:
          * hints: any decoded tag, even once and far away (ID exact, direction good);
          * cands: squares the detector found but could not read (too far), whose
            centre lies on the image horizon: every tag centre is at the camera's
            height (1.0 m), so real tags appear there and boxes/tables mostly do not."""
        rejected = [] if gray is None else cv2.aruco.detectMarkers(gray, DICT, parameters=PARAMS)[2]
        quads = []
        cx, cy, fx, fy = self.K[0, 2], self.K[1, 2], self.K[0, 0], self.K[1, 1]
        for r in rejected:
            q = r.reshape(4, 2)
            u, v = q.mean(0)
            side = float(np.mean([np.linalg.norm(q[i] - q[(i + 1) % 4]) for i in range(4)]))
            if 4.0 <= side <= 30.0 and abs(v - cy) < max(10.0, 0.8 * side):
                quads.append((u, v, side))
        if not found and not quads:
            return
        try:
            tf = self.tf_buffer.lookup_transform(self.map_frame, frame, stamp,
                                                 timeout=Duration(seconds=0.1))
        except tf2_ros.TransformException:
            return
        R = quat_to_matrix(tf.transform.rotation)
        t = tf.transform.translation
        cam = np.array([t.x, t.y, t.z])
        for tag_id, (tvec, _) in found.items():
            d = float(np.linalg.norm(tvec))
            p = R @ tvec + cam
            old = self.hints.get(tag_id)
            if old is None or d < old[2] + 0.3:
                self.hints[tag_id] = (float(p[0]), float(p[1]), d)
        for u, v, side in quads:
            rng = min(5.0, max(2.0, 0.12 * fx / side))     # rough: tag black square 0.12 m
            ray = np.array([(u - cx) / fx, (v - cy) / fy, 1.0])
            p = R @ (ray / np.linalg.norm(ray) * rng) + cam
            for c in self.cands:
                if math.hypot(c['x'] - p[0], c['y'] - p[1]) < 0.8:
                    c['x'] += (p[0] - c['x']) / (c['n'] + 1)
                    c['y'] += (p[1] - c['y']) / (c['n'] + 1)
                    c['n'] += 1
                    break
            else:
                self.cands.append({'x': float(p[0]), 'y': float(p[1]), 'n': 1, 'done': False})

    def approach_point(self, x, y, keep):
        """Drive towards (x, y) until about `keep` m away from it, then face it."""
        me = self.pose2d(self.map_frame)
        if me is None:
            return
        dx, dy = x - me[0], y - me[1]
        d = math.hypot(dx, dy)
        if d - keep > 0.3:
            step = d - keep
            self.goto(me[0] + dx / d * step, me[1] + dy / d * step)
        me = self.pose2d(self.map_frame)
        if me is not None and self.referee.running and not self.target_known():
            self.turn_to(math.atan2(y - me[1], x - me[0]))

    def next_unmeasured(self, exclude):
        """Nearest tag that has been read but not yet seen from within measure_distance."""
        if not bool(self.get_parameter('measure_all_tags').value):
            return None
        near = float(self.get_parameter('measure_distance').value)
        me = self.pose2d(self.map_frame)
        best = None
        for tid, h in list(self.hints.items()):
            if tid == exclude or self.measure_tries.get(tid, 0) >= 2:
                continue
            est = self.tags.get(tid)
            if est is not None and est.get('closest', 99.0) <= near:
                continue                                   # already measured well
            x, y = (est['x'], est['y']) if est is not None else (h[0], h[1])
            d = math.hypot(x - me[0], y - me[1]) if me else 0.0
            if best is None or d < best[0]:
                best = (d, tid, x, y)
        return best[1:] if best else None

    def next_candidate(self):
        need = int(self.get_parameter('candidate_min_hits').value)
        me = self.pose2d(self.map_frame)
        best = None
        for c in self.cands:
            if c['done'] or c['n'] < need:
                continue
            # next to a tag we already know: that is the tag, nothing new to find there
            if any(math.hypot(c['x'] - k['x'], c['y'] - k['y']) < 0.8 for k in self.tags.values()):
                c['done'] = True
                continue
            d = math.hypot(c['x'] - me[0], c['y'] - me[1]) if me else 0.0
            if best is None or d < best[0]:
                best = (d, c)
        return best[1] if best else None

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
        dist = float(np.linalg.norm(tvec))
        with self.rec_lock:
            lst = self.samples.setdefault(tag_id, [])
            lst.append((pos[0], pos[1], math.atan2(n[1], n[0]), dist))
            if len(lst) > 200:
                lst.pop(0)
            a = np.array(lst)
            # Far sightings get the ID right but the range badly wrong (a 1-pixel corner
            # error is metres at 3 m), so estimate only from the closest sightings so far.
            dmin = float(a[:, 3].min())
            a = a[a[:, 3] <= dmin + 0.5]
            est = {'x': float(np.median(a[:, 0])), 'y': float(np.median(a[:, 1])),
                   'facing_yaw': math.atan2(float(np.median(np.sin(a[:, 2]))),
                                            float(np.median(np.cos(a[:, 2])))),
                   'samples': len(lst), 'closest': dmin}
            est = self.fit_to_arena(est)
            first = tag_id not in self.tags
            if len(lst) >= int(self.get_parameter('min_samples').value):
                self.tags[tag_id] = est
                if first:
                    self.get_logger().info(
                        f'Found tag {tag_id} at ({est["x"]:.2f}, {est["y"]:.2f}), '
                        f'facing {math.degrees(est["facing_yaw"]):.0f} deg, seen from {dmin:.1f} m. '
                        f'Known: {sorted(self.tags)}')

    def fit_to_arena(self, est):
        """Far sightings can place a tag beyond a wall. A tag is inside the arena: pull it
        back onto the wall, and give a wall tag the wall's inward facing when the estimate is
        within 35 deg of it (wall tags always face straight into the arena)."""
        b = [float(v) for v in self.get_parameter('arena_bounds').value]
        if len(b) != 4:
            return est
        xmin, xmax, ymin, ymax = b
        x, y = min(max(est['x'], xmin), xmax), min(max(est['y'], ymin), ymax)
        walls = [(x - xmin, 0.0), (xmax - x, math.pi), (y - ymin, math.pi / 2), (ymax - y, -math.pi / 2)]
        gap, inward = min(walls)
        face = est['facing_yaw']
        if gap < 0.4 and abs(wrap(face - inward)) < math.radians(35):
            face = inward
            if inward in (0.0, math.pi):
                x = xmin if inward == 0.0 else xmax
            else:
                y = ymin if inward > 0 else ymax
        out = dict(est)
        out.update(x=x, y=y, facing_yaw=face)
        return out

    def on_wall(self, est):
        b = [float(v) for v in self.get_parameter('arena_bounds').value]
        return len(b) == 4 and (min(abs(est['x'] - b[0]), abs(est['x'] - b[1]),
                                    abs(est['y'] - b[2]), abs(est['y'] - b[3])) < 0.05)

    def forget(self, tag):
        """The tag was not where we thought: drop its position so it is searched again."""
        self.get_logger().warn(f'Tag {tag}: not found at its estimated position; '
                               'forgetting it and searching again.')
        with self.rec_lock:
            self.tags.pop(tag, None)
            self.samples.pop(tag, None)
        self.hints.pop(tag, None)
        self.measure_tries.pop(tag, None)

    def known(self, tag):
        with self.rec_lock:
            return tag in self.tags

    # ------------------------------------------------------------ exploration
    def spin_scan(self):
        """One full turn in place with the camera on."""
        speed = float(self.get_parameter('spin_speed').value)
        if not self.spin_is_clear():                      # make room before turning: forward
            if not self.turn_and_step('cramped before a scan spin', step=0.25) \
                    and self.front_close_now():
                self.reverse_gently(float(self.get_parameter('front_backoff').value))
        start = self.pose2d(self.odom_frame)
        if start is None:
            return
        turned, last = 0.0, start[2]
        end = self.now() + Duration(seconds=2 * math.pi / speed + 6.0)
        cmd = Twist()
        cmd.angular.z = speed
        while rclpy.ok() and self.referee.running and self.now() < end and turned < 2 * math.pi:
            t = getattr(self, 'current_target', None)
            if self.target_known() or (t is not None and t in self.hints):
                break                                      # stop early: next tag found / read
            if t is not None and self.next_unmeasured(exclude=t) is not None:
                break                                      # another tag read: go and measure it now
            me = self.pose2d(self.odom_frame)
            if me is not None:
                turned += abs(wrap(me[2] - last))
                last = me[2]
            self.cmd_pub.publish(cmd)
            time.sleep(0.05)
        self.stop()
        self.get_logger().info(f'Scan spin: turned {math.degrees(turned):.0f} deg.')

    def on_scan(self, msg):
        r = [x for x in msg.ranges if msg.range_min <= x <= msg.range_max]
        self.min_range = min(r) if r else None
        self.last_scan = msg

    def rear_clearance(self):
        """Free distance straight behind the robot's back edge (lidar, robot-width band),
        or None if unknown. The lidar only sees table BASES: tabletops overhang them, so the
        caller keeps an extra margin."""
        msg = getattr(self, 'last_scan', None)
        if msg is None:
            return None
        try:
            tf = self.tf_buffer.lookup_transform(self.base_frame, msg.header.frame_id, Time())
        except tf2_ros.TransformException:
            return None
        r = np.asarray(msg.ranges, dtype=float)
        a = msg.angle_min + np.arange(len(r)) * msg.angle_increment
        ok = np.isfinite(r) & (r >= msg.range_min) & (r <= msg.range_max)
        pts = np.stack([r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok]), np.zeros(ok.sum())], 1)
        R = quat_to_matrix(tf.transform.rotation)
        t = tf.transform.translation
        pts = pts @ R.T + np.array([t.x, t.y, t.z])
        rear_edge = float(self.get_parameter('rear_edge').value)
        half_w = float(self.get_parameter('half_width').value) + 0.05
        behind = pts[(pts[:, 0] < -rear_edge + 0.02) & (np.abs(pts[:, 1]) < half_w)]
        if not len(behind):
            return 4.0
        return float((-behind[:, 0]).min() - rear_edge)

    def back_out(self, distance, speed=None):
        """Replaces task_solution's reverse (0.3 m/s, blind to tabletops behind):
          * after a photo, or when Nav2 is stuck: turn in place to the most open direction
            and step forward (the mast stays put while turning, the cameras then look where
            the robot drives); only if nothing is open: a short, gentle, checked reverse;
          * line-up retry and anything else: a short (<= 0.2 m), gentle, checked reverse."""
        n = len(self.referee.reported)
        after_photo = n > getattr(self, '_reported_seen', 0)
        self._reported_seen = n
        stuck = abs(distance - float(self.get_parameter('back_out_distance').value)) < 1e-6
        if after_photo:
            self.turn_around_after_photo()
            return
        if stuck and self.turn_and_step('navigation stuck'):
            return
        if self.front_close_now():                          # only reason to reverse
            self.reverse_gently(float(self.get_parameter('front_backoff').value), speed)

    # ------------------------------------------------ front camera: reverse only if blocked
    def on_front_cloud(self, topic, m):
        """depth_obstacles clouds are in the base frame (x forward, y left, z up)."""
        close = False
        if m.width * m.height > 0:
            p = np.frombuffer(bytes(m.data), dtype=np.float32).reshape(-1, m.point_step // 4)[:, :3]
            front = 0.21                                     # m, base centre to front edge
            near = float(self.get_parameter('front_close').value)
            half_w = float(self.get_parameter('half_width').value) + 0.05
            close = bool(((p[:, 0] > front - 0.02) & (p[:, 0] < front + near)
                          & (np.abs(p[:, 1]) < half_w)).any())
        self.front_seen[topic] = (time.monotonic(), close)

    def front_close_now(self, max_age=0.5):
        now = time.monotonic()
        return any(c and now - t <= max_age for t, c in self.front_seen.values())

    def front_watchdog(self):
        """While Nav2 drives: something too close in front for front_close_s -> stop Nav2;
        the run thread then backs off (after_nav), and navigation carries on from there."""
        now = time.monotonic()
        if not getattr(self, '_ready', False) or not self.cmd_pub.nav_active() or self.pending_backoff:
            self.front_since = None
            return
        if not self.front_close_now():
            self.front_since = None
            return
        if self.front_since is None:
            self.front_since = now
            return
        if now - self.front_since >= float(self.get_parameter('front_close_s').value) \
                and now >= self.front_cooldown:
            self.get_logger().warn('Front camera: obstacle too close ahead (e.g. a tabletop); '
                                   'stopping Nav2 to back off a little.')
            self.pending_backoff = True
            self.front_cooldown = now + 8.0
            self.front_since = None
            self.cancel_all_nav()

    def after_nav(self):
        if self.pending_backoff:
            self.pending_backoff = False
            self.reverse_gently(float(self.get_parameter('front_backoff').value))

    def navigate(self, *args, **kwargs):
        result = super().navigate(*args, **kwargs)
        self.after_nav()
        return result

    def goto(self, *args, **kwargs):
        try:
            return self.goto_nav2(*args, **kwargs)
        finally:
            self.after_nav()

    def turn_around_after_photo(self, step=0.3):
        """After a reported tag: turn 180 deg on the spot (map heading, so odometry's turn
        error does not matter), then step forward if the lidar shows room."""
        # task_solution's visit() switched detection off before the photo: switch it back on,
        # or nothing seen during the turn and the sweep is recorded
        self.set_detecting(True)
        self.clear_tag_before_turn()
        frame = self.map_frame if self.pose2d(self.map_frame) is not None else self.odom_frame
        me = self.pose2d(frame)
        if me is None:
            return
        target = wrap(me[2] + math.pi)
        self.get_logger().info('Leaving the tag: turning 180 deg.')
        ok = self.turn_by_odom(target, tol=0.1, frame=frame)
        for _ in range(2):                                 # let the map heading catch up, then trim
            if not ok:
                break
            time.sleep(0.6)
            me = self.pose2d(frame)
            if me is None or abs(wrap(target - me[2])) < math.radians(5):
                break
            ok = self.turn_by_odom(target, tol=0.1, frame=frame)
        if not ok:
            self.get_logger().warn('Leaving the tag: the 180 deg turn was blocked; Nav2 takes over.')
            return
        ahead = [f for a, f in self.open_directions() if abs(a) < 1e-6]
        front = 0.21
        if ahead and ahead[0] >= front + step + 0.35:
            self.drive_straight(step)
        self.sweep_here()

    def clear_tag_before_turn(self, min_centre=0.55, cam_behind=0.05):
        """The rear corners swing 0.38 m from the centre while turning. If the photo was taken
        with the robot centre closer than min_centre to the tag, back off the difference
        (at most 0.12 m, gentle, checked behind) so the turn keeps >= 0.17 m clearance."""
        if not self.referee.reported:
            return
        with self.lock:
            det = self.detections.get(self.referee.reported[-1])
        if det is None or (self.now() - det[0]) > Duration(seconds=8.0):
            return
        tvec, n = np.asarray(det[1], float), np.asarray(det[2], float)
        centre = float(-tvec @ n) - cam_behind               # camera sits behind the centre
        if centre < min_centre:
            back = min(0.12, min_centre - centre)
            self.get_logger().info(f'Tag only {centre:.2f} m from the robot centre: backing off '
                                   f'{back:.2f} m before turning.')
            self.reverse_gently(back)

    def sweep_here(self):
        """Full 360 deg turn on the spot with detection on, recording every tag in view (no
        early stop). Skipped when every tag still to visit is already known."""
        missing = [t for t in self.referee.remaining_tags if not self.known(t)]
        if not missing:
            self.get_logger().info('Sweep skipped: all remaining tags are known.')
            return
        self.set_detecting(True)
        if not self.spin_is_clear():
            self.turn_and_step('cramped before a sweep', step=0.25)
        speed = float(self.get_parameter('spin_speed').value)
        start = self.pose2d(self.odom_frame)
        if start is None:
            return
        turned, last = 0.0, start[2]
        end = time.monotonic() + 2 * math.pi / speed + 10.0
        cmd = Twist()
        cmd.angular.z = speed
        while rclpy.ok() and self.referee.running and time.monotonic() < end and turned < 2 * math.pi:
            me = self.pose2d(self.odom_frame)
            if me is not None:
                turned += abs(wrap(me[2] - last))
                last = me[2]
            self.cmd_pub.publish(cmd)
            time.sleep(0.05)
        self.stop()
        self.get_logger().info(f'Sweep after the tag: turned {math.degrees(turned):.0f} deg; '
                               f'looking for {missing}; known: {sorted(self.tags)}.')

    def open_directions(self, step_deg=30):
        """[(angle rad in the robot frame, free m ahead in a robot-wide corridor)] from the
        lidar, or [] if there is no scan."""
        msg = getattr(self, 'last_scan', None)
        if msg is None:
            return []
        try:
            tf = self.tf_buffer.lookup_transform(self.base_frame, msg.header.frame_id, Time())
        except tf2_ros.TransformException:
            return []
        r = np.asarray(msg.ranges, dtype=float)
        a = msg.angle_min + np.arange(len(r)) * msg.angle_increment
        ok = np.isfinite(r) & (r >= msg.range_min) & (r <= msg.range_max)
        pts = np.stack([r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok]), np.zeros(ok.sum())], 1)
        R = quat_to_matrix(tf.transform.rotation)
        t = tf.transform.translation
        pts = (pts @ R.T + np.array([t.x, t.y, t.z]))[:, :2]
        half_w = float(self.get_parameter('half_width').value) + 0.05
        out = []
        for ang in np.radians(np.arange(-180, 180, step_deg)):
            d = np.array([math.cos(ang), math.sin(ang)])
            along = pts @ d
            lateral = np.abs(pts @ np.array([-d[1], d[0]]))
            blk = along[(along > 0) & (lateral < half_w)]
            out.append((float(ang), float(blk.min()) if len(blk) else 4.0))
        return out

    def turn_and_step(self, why, step=0.3):
        """Turn in place to the most open direction (small turns preferred) and drive
        forward `step` m. False if no direction has room (caller then reverses gently)."""
        front = 0.21                                         # m, base centre to front edge
        need = front + step + 0.35
        dirs = [(a, f) for a, f in self.open_directions() if f >= need]
        if not dirs:
            return False
        ang, free = max(dirs, key=lambda af: min(af[1], 2.5) - 0.6 * abs(af[0]) / math.pi)
        frame = self.map_frame if self.pose2d(self.map_frame) is not None else self.odom_frame
        me = self.pose2d(frame)
        if me is None:
            return False
        self.get_logger().info(f'{why}: turning {math.degrees(ang):+.0f} deg to open space '
                               f'({free:.1f} m free) and stepping forward instead of reversing.')
        if abs(ang) > math.radians(10) and not self.turn_by_odom(me[2] + ang, tol=0.1, frame=frame):
            return False
        self.drive_straight(min(step, free - front - 0.35))
        return True

    def reverse_gently(self, distance, speed=None):
        """Gentle reverse: ramps up and down, and never reverses further than the lidar
        clearance behind minus a margin for overhanging tabletops the lidar cannot see.
        The collision monitor still applies."""
        speed = float(self.get_parameter('back_out_speed').value) if speed is None else min(
            float(speed), float(self.get_parameter('back_out_speed').value))
        margin = float(self.get_parameter('back_out_margin').value)
        clear = self.rear_clearance()
        if clear is not None:
            room = clear - margin
            if room < 0.05:
                self.get_logger().warn(f'Not reversing: only {clear:.2f} m free behind '
                                       f'(keeping {margin:.2f} m for tabletops).')
                return
            if room < distance:
                self.get_logger().info(f'Reversing {room:.2f} m instead of {distance:.2f} m '
                                       f'({clear:.2f} m free behind).')
                distance = room
        start = self.pose2d(self.odom_frame)
        if start is None or distance <= 0.0:
            return
        accel = 0.3                                          # m/s^2 up and down
        end = time.monotonic() + distance / speed + 6.0
        v = 0.0
        cmd = Twist()
        while rclpy.ok() and self.referee.running and time.monotonic() < end:
            me = self.pose2d(self.odom_frame)
            if me is None:
                break
            left = distance - math.hypot(me[0] - start[0], me[1] - start[1])
            if left <= 0.01:
                break
            target = min(speed, max(0.04, math.sqrt(2 * accel * left)))   # brake before the end
            v = min(target, v + accel * 0.05)
            cmd.linear.x = -v
            self.cmd_pub.publish(cmd)
            time.sleep(0.05)
        self.stop()

    def spin_is_clear(self):
        c = float(self.get_parameter('spin_clearance').value)
        return self.min_range is not None and self.min_range >= c

    def target_known(self):
        t = getattr(self, 'current_target', None)
        return t is not None and self.known(t)

    def goto_nav2(self, x, y, stop_when_known=True, interrupt_on_new_tag=False, timeout=None):
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
        deadline = self.now() + Duration(seconds=float(
            timeout if timeout is not None else self.get_parameter('waypoint_timeout_s').value))
        # Stuck = the robot has not MOVED 0.1 m for drive_stuck_s. (Not "not getting closer":
        # a detour around a table first moves away from the goal, and that is progress.)
        stuck_time = Duration(seconds=float(self.get_parameter('drive_stuck_s').value))
        reached = float(self.get_parameter('waypoint_reached').value)
        anchor, anchor_at = None, self.now()
        seen_at_start = set(self.hints)
        tgt = getattr(self, 'current_target', None)
        while rclpy.ok() and not res.done():
            me = self.pose2d(self.map_frame)
            d = math.hypot(x - me[0], y - me[1]) if me is not None else None
            new_ids = set(self.hints) - seen_at_start
            if (tgt is not None and tgt in new_ids) or (interrupt_on_new_tag and new_ids):
                self.get_logger().info(f'Tag {sorted(new_ids)} read while driving; going to it now.')
                handle.cancel_goal_async()
                self.cancel_all_nav()
                return
            stop = (not self.referee.running or self.now() > deadline
                    or (stop_when_known and self.target_known())
                    or (d is not None and d <= reached))
            if me is not None:
                if anchor is None or math.hypot(me[0] - anchor[0], me[1] - anchor[1]) > 0.10 \
                        or abs(math.atan2(math.sin(me[2] - anchor[2]), math.cos(me[2] - anchor[2]))) > 0.3:
                    anchor, anchor_at = me, self.now()
                elif self.now() - anchor_at > stuck_time:
                    self.get_logger().warn(f'Goal ({x:.1f}, {y:.1f}): robot not moving; skipping.')
                    stop = True
            if stop:
                handle.cancel_goal_async()
                self.cancel_all_nav()
                return
            time.sleep(0.05)
        if res.result() is not None and res.result().status != GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f'Sweep point ({x:.1f}, {y:.1f}) not reachable; next one.')

    def close_in(self, tag):
        """Seen only from far away: the direction is right but the range is not. Drive
        towards it until it is about `confirm_distance` away, so the position is
        re-measured from close up before the visit relies on it."""
        want = float(self.get_parameter('confirm_distance').value)
        for _ in range(2):
            with self.rec_lock:
                est = dict(self.tags[tag])
            if est.get('closest', 0.0) <= want + 0.3 or not self.referee.running:
                return
            if self.on_wall(est):
                return       # wall tag: facing and wall distance are fixed by the arena walls
            me = self.pose2d(self.map_frame)
            if me is None:
                return
            dx, dy = est['x'] - me[0], est['y'] - me[1]
            d = math.hypot(dx, dy)
            step = max(0.0, min(d - want, 2.0))
            if step < 0.3:
                return
            gx, gy = me[0] + dx / d * step, me[1] + dy / d * step
            self.get_logger().info(
                f'Tag {tag}: only seen from {est["closest"]:.1f} m; moving {step:.1f} m closer '
                'to confirm it and measure its position.')
            self.set_detecting(True)
            self.goto(gx, gy, stop_when_known=False, timeout=20.0)
            # look at it again from here
            with self.rec_lock:
                est = dict(self.tags[tag])
            me = self.pose2d(self.map_frame)
            if me is not None:
                self.turn_to(math.atan2(est['y'] - me[1], est['x'] - me[0]))

    def opening_moves(self):
        """The `opening` moves, one after the other; the camera records tags meanwhile."""
        text = str(self.get_parameter('opening').value).strip()
        if not text:
            return
        log = self.get_logger()
        steps = []
        for part in text.replace(';', ',').split(','):
            words = part.split()
            if len(words) != 2 or words[0] not in ('forward', 'back', 'left', 'right'):
                log.error(f'opening: cannot read "{part.strip()}" (use e.g. "forward 1.3, left 90"); '
                          'skipping the opening.')
                return
            steps.append((words[0], float(words[1])))
        log.info(f'Opening moves: {text}.')
        for what, amount in steps:
            if not self.referee.running:
                return
            if what in ('forward', 'back'):
                ok = self.drive_straight(amount if what == 'forward' else -amount)
            else:
                # turn in the map frame (SLAM/AMCL correct the heading with the lidar;
                # wheel odometry over-reports turns: 90 deg odom = ~67 deg real in the sim)
                frame = self.map_frame if self.pose2d(self.map_frame) is not None else self.odom_frame
                me = self.pose2d(frame)
                if me is None:
                    return
                target = me[2] + math.radians(amount) * (1.0 if what == 'left' else -1.0)
                ok = self.turn_by_odom(target, frame=frame)
                for _ in range(2):                     # let the map frame catch up, then trim
                    if not ok:
                        break
                    time.sleep(0.8)
                    me = self.pose2d(frame)
                    if me is None or abs(wrap(target - me[2])) < math.radians(3):
                        break
                    ok = self.turn_by_odom(target, frame=frame)
            if not ok:
                log.warn(f'Opening: "{what} {amount:g}" was blocked; starting the search from here.')
                return
        log.info('Opening done; starting the search.')

    def drive_straight(self, dist, speed=0.25, blocked_s=3.0):
        """Drive dist m along the current heading (odometry, heading held). False if the
        collision monitor (or anything) kept the robot from moving for blocked_s."""
        start = self.pose2d(self.odom_frame)
        if start is None:
            return False
        yaw0 = start[2]
        last_move, last_pos = time.monotonic(), start
        end = time.monotonic() + abs(dist) / speed + 10.0
        cmd = Twist()
        while rclpy.ok() and self.referee.running and time.monotonic() < end:
            me = self.pose2d(self.odom_frame)
            if me is None:
                break
            done = math.hypot(me[0] - start[0], me[1] - start[1])
            left = abs(dist) - done
            if left <= 0.02:
                self.stop()
                return True
            if math.hypot(me[0] - last_pos[0], me[1] - last_pos[1]) > 0.03:
                last_move, last_pos = time.monotonic(), me
            elif time.monotonic() - last_move > blocked_s:
                break
            cmd.linear.x = math.copysign(min(speed, max(0.06, 1.5 * left)), dist)
            cmd.angular.z = max(-0.5, min(0.5, 2.0 * wrap(yaw0 - me[2])))
            self.cmd_pub.publish(cmd)
            time.sleep(0.05)
        self.stop()
        return False

    def turn_by_odom(self, yaw, tol=0.05, blocked_s=3.0, frame=None):
        """Turn in place to heading yaw in `frame` (default odom). False if blocked."""
        frame = frame or self.odom_frame
        start = self.pose2d(frame)
        if start is None:
            return False
        last_move, last_yaw = time.monotonic(), start[2]
        end = time.monotonic() + abs(wrap(yaw - start[2])) / 0.3 + 10.0
        cmd = Twist()
        while rclpy.ok() and self.referee.running and time.monotonic() < end:
            me = self.pose2d(frame)
            if me is None:
                break
            err = wrap(yaw - me[2])
            if abs(err) < tol:
                self.stop()
                return True
            if abs(wrap(me[2] - last_yaw)) > 0.05:
                last_move, last_yaw = time.monotonic(), me[2]
            elif time.monotonic() - last_move > blocked_s:
                break
            cmd.angular.z = math.copysign(min(0.8, max(0.2, 1.5 * abs(err))), err)
            self.cmd_pub.publish(cmd)
            time.sleep(0.05)
        self.stop()
        return False

    def turn_to(self, yaw, tol=0.15, timeout=8.0):
        end = self.now() + Duration(seconds=timeout)
        while rclpy.ok() and self.referee.running and self.now() < end:
            me = self.pose2d(self.map_frame)
            if me is None:
                break
            err = wrap(yaw - me[2])
            if abs(err) < tol:
                break
            cmd = Twist()
            cmd.angular.z = max(-0.8, min(0.8, 2.0 * err))
            if abs(cmd.angular.z) < 0.2:
                cmd.angular.z = math.copysign(0.2, err)
            self.cmd_pub.publish(cmd)
            time.sleep(0.05)
        self.stop()
        self.sleep(0.5)                                    # let the camera see it a few times

    def good_enough(self, tag, max_age=0.5):
        """True if the latest sighting already meets the visit rule with margin."""
        with self.lock:
            det = self.detections.get(tag)
        if det is None or (self.now() - det[0]) > Duration(seconds=max_age):
            return False
        tvec, n = np.asarray(det[1], float), np.asarray(det[2], float)
        cam = -tvec                                          # camera seen from the tag
        along = float(cam @ n)                               # distance out along the face normal
        lateral = float(np.linalg.norm(cam - along * n))
        off = math.degrees(math.acos(max(-1.0, min(1.0, -float(n[2])))))
        lo, hi = [float(v) for v in self.get_parameter('accept_cam_range').value]
        return (lo <= along <= hi and off <= float(self.get_parameter('accept_angle_deg').value)
                and lateral <= float(self.get_parameter('accept_lateral').value))

    def align(self, tag):
        """task_solution's camera line-up (polar pose controller), plus: stop and report as
        soon as the pose already meets the rule with margin, instead of turning on to hit
        the tighter internal tolerance."""
        max_v = float(self.get_parameter('max_linear').value)
        max_w = float(self.get_parameter('max_angular').value)
        pos_tol = float(self.get_parameter('pos_tolerance').value)
        yaw_tol = float(self.get_parameter('yaw_tolerance').value)
        deadline = self.now() + Duration(seconds=float(self.get_parameter('align_timeout_s').value))
        target, in_place, rate = None, False, 0.05
        started = self.now()
        self.align_saw_tag = False
        while rclpy.ok() and self.referee.running:
            if self.good_enough(tag):
                self.stop()
                self.get_logger().info(f'Tag {tag}: pose is within the rules; taking the picture.')
                return True
            if self.now() > deadline:
                self.stop()
                self.get_logger().warn(f'Tag {tag}: alignment timed out.')
                return target is not None
            live = self.live_target(tag)
            if live is not None:
                self.align_saw_tag = True
            elif target is None and (self.now() - started) > Duration(seconds=4.0):
                # Not where we expected it: sweep in place instead of staring at a stale spot.
                cmd = Twist()
                cmd.angular.z = 0.5
                self.cmd_pub.publish(cmd)
                time.sleep(rate)
                continue
            if live is not None:
                new = live[0]
                target = new if target is None else (
                    target[0] + 0.3 * (new[0] - target[0]), target[1] + 0.3 * (new[1] - target[1]),
                    wrap(target[2] + 0.3 * wrap(new[2] - target[2])))
            me = self.pose2d(self.odom_frame)
            if me is None or target is None:
                if me is not None and target is None and tag in self.tags:   # look towards it
                    mp = self.pose2d(self.map_frame)
                    if mp is not None:
                        t = self.tags[tag]
                        err = wrap(math.atan2(t['y'] - mp[1], t['x'] - mp[0]) - mp[2])
                        cmd = Twist()
                        cmd.angular.z = math.copysign(min(max_w, max(0.15, abs(err))), err)
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
                alpha, beta, direction = wrap(heading - me[2]), wrap(tyaw - heading), 1.0
                if abs(alpha) > math.pi / 2:
                    alpha, beta, direction = wrap(alpha - math.pi), wrap(beta - math.pi), -1.0
                cmd.angular.z = max(-max_w, min(max_w, 2.5 * alpha - 0.8 * beta))
                cmd.linear.x = direction * min(max_v, 1.2 * dist + 0.03) * max(0.0, math.cos(min(abs(alpha), 1.4)))
            else:
                err = wrap(tyaw - me[2])
                if abs(err) <= yaw_tol:
                    self.stop()
                    return True
                cmd.angular.z = max(-max_w, min(max_w, 2.5 * err))
                if abs(cmd.angular.z) < 0.15:
                    cmd.angular.z = math.copysign(0.15, err)
            self.cmd_pub.publish(cmd)
            time.sleep(rate)
        self.stop()
        return False

    def capture(self, tag, timeout=3.0):
        """Photo for the TagVisit: the newest confirmed frame of this tag taken after
        the robot stopped (allowing for the camera pipeline lag), at a sensible range
        and angle. Reports even when the fine alignment timed out, as long as the tag
        is clearly in view; the judges decide whether the visit scores."""
        lag = Duration(seconds=float(self.get_parameter('camera_lag_s').value))
        after = self.now() - lag
        end = self.now() + Duration(seconds=timeout)
        while rclpy.ok() and self.now() < end:
            with self.lock:
                det = self.detections.get(tag)
            if det is not None and det[0] > after:
                img, tvec, normal = det[4], det[1], det[2]
                rng = float(np.linalg.norm(tvec))
                off = math.degrees(math.acos(max(-1.0, min(1.0, -float(normal[2])))))
                if 0.35 <= rng <= 0.8 and off <= 12.0:
                    return img, (rng, off)
            time.sleep(0.03)
        return None, None

    def explore_until_known(self, tag):
        """Find `tag`, cheapest clue first:
          1. it was decoded at least once (ID exact): drive towards it;
          2. an unread tag-like square was seen several times in one place: go and look;
          3. otherwise the next sweep point, with a scan spin there."""
        log = self.get_logger()
        self.current_target = tag
        self.set_detecting(True)
        tries_hint = 0
        cands_checked = 0
        max_c = int(self.get_parameter('max_candidates_per_tag').value)
        try:
            while rclpy.ok() and self.referee.running and not self.known(tag):
                hint = self.hints.get(tag)
                if hint is not None and tries_hint < 4:
                    tries_hint += 1
                    log.info(f'Tag {tag}: read once from {hint[2]:.1f} m; heading there to confirm it '
                             f'[{tries_hint}/4].')
                    self.approach_point(hint[0], hint[1], keep=1.3)
                    if not self.known(tag):               # face where it was seen and look
                        me = self.pose2d(self.map_frame)
                        if me is not None:
                            self.turn_to(math.atan2(hint[1] - me[1], hint[0] - me[0]))
                        self.sleep(1.5)
                    continue
                other = self.next_unmeasured(exclude=tag)
                if other is not None:
                    tid, ox, oy = other
                    self.measure_tries[tid] = self.measure_tries.get(tid, 0) + 1
                    log.info(f'Looking for tag {tag}: tag {tid} spotted; going to measure it '
                             f'(not reporting it yet), then scanning from there.')
                    self.approach_point(ox, oy, keep=1.3)
                    if not self.known(tag) and self.referee.running:
                        self.spin_scan()
                    continue
                cand = self.next_candidate() if cands_checked < max_c else None
                if cand is not None:
                    cands_checked += 1
                    cand['done'] = True
                    log.info(f'Looking for tag {tag}: checking an unread tag-like square near '
                             f'({cand["x"]:.1f}, {cand["y"]:.1f}) (seen {cand["n"]}x).')
                    self.approach_point(cand['x'], cand['y'], keep=1.5)
                    continue
                if self.next_wp >= len(self.sweep):
                    break
                x, y = self.sweep[self.next_wp]
                self.next_wp += 1
                log.info(f'Looking for tag {tag}: no clues; sweep point {self.next_wp}/{len(self.sweep)}'
                         f' ({x:.1f}, {y:.1f}). Known so far: {sorted(self.tags)}')
                self.goto(x, y, interrupt_on_new_tag=True)   # drop the sweep point if a tag is read
                if not self.known(tag) and self.referee.running and not self.hints.get(tag):
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
            self._reported_seen = len(self.referee.reported)
            self.opening_moves()
            self.spin_scan()
            for tag in order:
                if not self.referee.running:
                    break
                if tag in self.referee.reported:
                    continue
                # try the tag whose turn it is twice before moving on (keeps the order);
                # the positions of all other tags are kept
                attempts = max(1, int(self.get_parameter('visit_attempts').value))
                for attempt in range(1, attempts + 1):
                    if not self.referee.running or tag in self.referee.reported:
                        break
                    if not self.known(tag) and not self.explore_until_known(tag):
                        log.warn(f'Tag {tag}: not found after the whole sweep; skipping it for now.')
                        break
                    if attempt > 1:
                        log.warn(f'Tag {tag}: trying again [attempt {attempt}/{attempts}].')
                    self.close_in(tag)
                    self.visit(tag)
                    self.set_detecting(True)               # keep recording tags afterwards
                    if tag not in self.referee.reported and not getattr(self, 'align_saw_tag', True):
                        self.forget(tag)                   # only this tag: it was not there
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
