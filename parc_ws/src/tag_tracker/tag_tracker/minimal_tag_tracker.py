"""Minimal fallback solution: no Nav2, no SLAM, no costmaps.

    ros2 launch tag_tracker tag_tracker.launch.py                                     # sim
    ros2 launch tag_tracker tag_tracker.launch.py use_sim_time:=false base_frame:=base_link   # robot
    ros2 run task_solution start_run        # after the judge arms the run

Like green_nav (colour target + depth -> 3D goal), but for AprilTags and without Nav2:

  Vision   apriltag_ros (parcbot_docking pipeline, TF tag_N; reads tags from far away) or
           OpenCV AprilTag 36h11 (detector:=opencv), IDs 1/4/7/9 exact codes only; the
           distance to tags farther than 1 m comes from the depth image at the tag's centre
           pixel. Every tag seen is stored in the odom frame (median of the closest sightings).
  Driving  Potential field: the goal attracts, obstacle points repel (lidar /scan_filtered +
           the depth-camera 3D points from depth_obstacles, which include tabletops). The
           robot veers around obstacles instead of stopping. A hard front guard stops forward
           motion if anything is within front_stop of the bumper.
  States   WAIT -> per tag in the referee's order:
             visible now          -> APPROACH (live camera) -> ALIGN -> REPORT -> BACK_OUT
             remembered (odom)    -> GOTO_MEMORY -> (not visible on arrival) SWEEP 360
             unknown              -> SEARCH: spin 360, then wander towards open space it has
                                     not been to yet (breadcrumb memory), repeat
  Photo    taken as soon as a fresh sighting meets the rule with margin (camera 0.49-0.61 m
           out along the tag normal, <= 8 deg, <= 8 cm lateral) - no slow final squaring.
  Recovery commanded forward but not moving for stuck_time -> back up + turn to open side.

Live tuning without restarting, e.g.:
    ros2 param set /tag_tracker max_linear_x 0.2
    ros2 param set /tag_tracker repulsive_gain 0.08
"""

import bisect
import math
import threading
import time

import numpy as np
import rclpy
import tf2_ros
from cv_bridge import CvBridge
from apriltag_msgs.msg import AprilTagDetectionArray
from geometry_msgs.msg import Twist, TwistStamped
from nav_msgs.msg import Odometry
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import CameraInfo, Image, Imu, LaserScan, PointCloud2

from task_solution.referee import VISIT_HOLD_S, RefereeClient
from task_solution.tag_mapper import detect_tags, quat_to_matrix


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


class MinimalTagTracker(Node):

    def __init__(self):
        super().__init__('tag_tracker')
        P = {
            # --- live-tunable motion ---
            'max_linear_x': 0.25,        # m/s
            'max_angular_z': 0.8,        # rad/s
            'attractive_gain': 1.0,
            'repulsive_gain': 0.05,
            'influence_distance': 0.7,   # m beyond the robot's radius where obstacles repel
            'robot_radius': 0.30,        # m (footprint 0.51 x 0.46)
            'cloud_memory_s': 3.0,       # s depth-camera obstacles are remembered (0 = live only)
            'front_stop': 0.12,          # m from the front bumper: no forward motion
            'heading_gain': 1.8,
            'search_spin_speed': 0.4,    # rad/s
            'wander_distance': 1.5,      # m per wander step
            'wander_time': 8.0,          # s max per wander step
            'stuck_time': 3.0,           # s commanded forward without moving = trapped
            'progress_time': 6.0,        # s without getting 0.15 m closer -> detour
            # --- tags ---
            'standoff': 0.5,             # m, robot centre to tag (rule)
            'approach_extra': 0.35,      # m: first aim this much farther out, then close in
            'pos_tolerance': 0.08,
            'close_in_repulsion': 0.15,  # repulsion scale for the last few cm (walls next to tags)
            'yaw_tolerance_deg': 4.0,
            'tag_size': 0.12,            # black square edge, m
            'tag_ids': [1, 4, 7, 9],
            'depth_min_range': 1.0,
            'memory_reach': 0.35,        # m: arrived at a remembered approach point
            'detector': 'apriltag',      # apriltag (apriltag_ros + TF) or opencv
            'detections_topic': '/camera1/camera1/color/detections',
            'tag_frame_prefix': 'tag_',
            'accept_cam_range': [0.51, 0.59],   # m camera -> tag plane (target ~0.55): take the photo
            'accept_angle_deg': 8.0,
            'accept_lateral': 0.08,
            'novelty_gain': 1.0,         # wander: preference for places not yet visited
            'record_max_yaw_rate': 0.15,  # rad/s: tag positions are only stored when turning slower
            'record_max_yaw_rate_imu': 0.7,  # gyro pose: still stored (for discovery), still ones win
            'sweep_step_deg': 45.0,      # sweep: turn this much, then hold still briefly to look
            'sweep_pause': 0.6,          # s
            # --- topics / frames ---
            'image_topic': '/camera1/camera1/color/image_raw',
            'camera_info_topic': '/camera1/camera1/color/camera_info',
            'depth_topic': '/camera1/camera1/depth/image_rect_raw',
            'scan_topic': '/scan_filtered',
            'cloud_topics': ['/depth_obstacles/camera1', '/depth_obstacles/camera2'],
            'odom_topic': '/botwheel_explorer/odom',
            'cmd_vel_topic': '/cmd_vel',
            'stamped': False,            # True on the robot: TwistStamped (botwheel_explorer)
            'stamp_frame': 'base_link',
            'pose_source': 'auto',       # auto: gyro+wheel speed if imu_topic publishes, else TF
            'imu_topic': '/camera1/camera1/imu',
            'odom_frame': 'odom',        # frame for pose + tag memory: 'map' with live SLAM
            'base_frame': 'base_footprint',
        }
        for k, v in P.items():
            self.declare_parameter(k, v)
        g = self.p

        self.bridge = CvBridge()
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.referee = RefereeClient(self)
        self.lock = threading.Lock()

        self.K = None
        self.D = None
        self.pose = None                 # (x, y, yaw) in odom_frame
        self.speed = 0.0
        self.last_depth = None
        self.scan_pts = np.zeros((0, 2))
        self.cloud_pts = {}
        self.cloud_mem = {}              # (ix, iy) 5 cm world cell -> last seen (monotonic s)
        self.live = {}                   # id -> dict(t, x, y, facing, rng, img)
        self.samples = {}                # id -> list of (x, y, facing, rng)
        self.memory = {}                 # id -> dict(x, y, facing, closest)
        self.last_detect = 0.0
        self.last_cmd = Twist()
        self.status = 'WAIT'
        self.dbg = None
        self.progress = None
        self.yaw_rate = 0.0
        self.mode = None                 # 'imu' (own gyro/wheel pose) or 'tf'; decided at start
        self.est = [0.0, 0.0, 0.0]       # gyro/wheel dead reckoning (x, y, yaw)
        self.hist = []                   # (stamp ns, x, y, yaw) of the estimate, last few s
        self.imu_R = None
        self.imu_t = None
        self.imu_seen = 0
        self.odom_t = None
        self.img_buf = {}                # stamp ns -> colour image (apriltag_ros pairing)
        self.crumbs = []                 # odom (x, y) every 0.3 m driven: where we have been

        self.cmd_pub = self.create_publisher(TwistStamped if g('stamped') else Twist,
                                             g('cmd_vel_topic'), 10)
        self.create_subscription(AprilTagDetectionArray, g('detections_topic'), self.on_apriltag,
                                 qos_profile_sensor_data)
        self.create_subscription(Odometry, g('odom_topic'), self.on_odom, 20)
        if g('pose_source') != 'tf':
            self.create_subscription(Imu, g('imu_topic'), self.on_imu, qos_profile_sensor_data)
        self.t_start = time.monotonic()
        self.create_timer(0.5, self.decide_mode)
        self.create_subscription(CameraInfo, g('camera_info_topic'), self.on_info, qos_profile_sensor_data)
        self.create_subscription(Image, g('image_topic'), self.on_image, qos_profile_sensor_data)
        self.create_subscription(Image, g('depth_topic'), lambda m: setattr(self, 'last_depth', m),
                                 qos_profile_sensor_data)
        self.create_subscription(LaserScan, g('scan_topic'), self.on_scan, qos_profile_sensor_data)
        for t in g('cloud_topics'):
            self.create_subscription(PointCloud2, t, lambda m, t=t: self.on_cloud(t, m),
                                     qos_profile_sensor_data)
        self.create_timer(0.05, self.update_pose)
        self.create_timer(3.0, self.log_status)
        self.get_logger().info('Minimal tag tracker ready (no Nav2). Waiting for the referee.')
        threading.Thread(target=self.run, daemon=True).start()

    def p(self, name):
        return self.get_parameter(name).value

    # ================================================================ inputs
    def decide_mode(self):
        if self.mode is not None:
            return
        src = self.p('pose_source')
        waited = time.monotonic() - self.t_start
        if src == 'tf' or (src == 'auto' and self.imu_seen <= 20 and waited > 10.0):
            self.mode = 'tf'
        elif self.imu_seen > 20:
            self.mode = 'imu'
        else:
            return                                            # keep waiting for IMU data
        self.est = [0.0, 0.0, 0.0]
        self.hist = []
        self.get_logger().info(
            'Pose: gyro heading + wheel speed (wheel odometry yaw is not used).' if self.mode == 'imu'
            else f'Pose: TF {self.p("odom_frame")} -> {self.p("base_frame")} (no IMU data).')

    def on_imu(self, m):
        if self.imu_R is None:
            T = self.to_base(m.header.frame_id)
            if T is None:
                return
            self.imu_R = T[0]
        t = Time.from_msg(m.header.stamp).nanoseconds * 1e-9
        w = self.imu_R @ np.array([m.angular_velocity.x, m.angular_velocity.y, m.angular_velocity.z])
        if self.imu_t is not None and 0.0 < t - self.imu_t < 0.2:
            self.est[2] = wrap(self.est[2] + float(w[2]) * (t - self.imu_t))
        self.imu_t = t
        self.imu_seen += 1

    def on_odom(self, m):
        self.speed = math.hypot(m.twist.twist.linear.x, m.twist.twist.linear.y)
        # turn rate for the 'still' check: wheel odometry (smooth; its ~13 % scale error does
        # not matter here, while single gyro samples are too noisy for a threshold)
        self.yaw_rate = m.twist.twist.angular.z
        if self.mode != 'imu':
            return
        st = Time.from_msg(m.header.stamp).nanoseconds
        t = st * 1e-9
        if self.odom_t is not None and 0.0 < t - self.odom_t < 0.5:
            dt = t - self.odom_t
            c, s_ = math.cos(self.est[2]), math.sin(self.est[2])
            vx, vy = m.twist.twist.linear.x, m.twist.twist.linear.y
            self.est[0] += (c * vx - s_ * vy) * dt
            self.est[1] += (s_ * vx + c * vy) * dt
        self.odom_t = t
        self.hist.append((st, self.est[0], self.est[1], self.est[2]))
        del self.hist[:-400]
        self.set_pose(tuple(self.est))

    def pose_at(self, stamp_ns):
        """Estimated pose at a past stamp (nearest sample, imu mode)."""
        h = self.hist
        if not h:
            return None
        i = bisect.bisect_left([e[0] for e in h], stamp_ns)
        cand = [h[j] for j in (i - 1, i) if 0 <= j < len(h)]
        best = min(cand, key=lambda e: abs(e[0] - stamp_ns))
        return best[1:] if abs(best[0] - stamp_ns) < 3e8 else None

    def set_pose(self, pose):
        self.pose = pose
        if self.referee.running and (not self.crumbs or math.hypot(
                pose[0] - self.crumbs[-1][0], pose[1] - self.crumbs[-1][1]) > 0.3):
            self.crumbs.append(pose[:2])

    def update_pose(self):
        """Robot pose in odom_frame from TF ('map' with live SLAM: heading stays right after
        many spins; raw wheel odometry drifts in yaw with every 360 deg sweep)."""
        if self.mode != 'tf':
            return
        try:
            tf = self.tf_buffer.lookup_transform(self.p('odom_frame'), self.p('base_frame'), Time())
        except tf2_ros.TransformException:
            return
        t, q = tf.transform.translation, tf.transform.rotation
        self.set_pose((t.x, t.y, math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))))

    def on_info(self, m):
        if self.K is None:
            self.K = np.array(m.k, dtype=float).reshape(3, 3)
            self.D = np.array(m.d, dtype=float)

    def to_base(self, frame):
        """Static transform base <- frame (sensors are fixed to the robot)."""
        try:
            tf = self.tf_buffer.lookup_transform(self.p('base_frame'), frame, Time())
        except tf2_ros.TransformException:
            return None
        t = tf.transform.translation
        return quat_to_matrix(tf.transform.rotation), np.array([t.x, t.y, t.z])

    def on_scan(self, m):
        r = np.asarray(m.ranges, dtype=float)
        a = m.angle_min + np.arange(len(r)) * m.angle_increment
        ok = np.isfinite(r) & (r >= m.range_min) & (r <= min(m.range_max, 4.0))
        pts = np.stack([r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok]), np.zeros(ok.sum())], 1)
        T = self.to_base(m.header.frame_id)
        if T is not None:
            pts = pts @ T[0].T + T[1]
        self.scan_pts = pts[:, :2]

    def on_cloud(self, topic, m):
        if m.width == 0:
            self.cloud_pts[topic] = np.zeros((0, 2))
            return
        p = np.frombuffer(bytes(m.data), dtype=np.float32).reshape(-1, 3)[::4]
        if m.header.frame_id != self.p('base_frame'):
            T = self.to_base(m.header.frame_id)
            if T is None:
                return
            p = p @ T[0].T + T[1]
        p = p[np.hypot(p[:, 0], p[:, 1]) < 3.0]
        self.cloud_pts[topic] = p[:, :2]
        # remember them in the world frame for a few s: the cameras only see ahead, and without
        # memory every turn would make obstacles vanish/appear and the field flip back and forth
        if self.pose is None or not len(p):
            return
        px, py, pyaw = self.pose
        c, s_ = math.cos(pyaw), math.sin(pyaw)
        wx = px + c * p[:, 0] - s_ * p[:, 1]
        wy = py + s_ * p[:, 0] + c * p[:, 1]
        keys = np.unique(np.stack([np.round(wx / 0.05), np.round(wy / 0.05)], 1).astype(int), axis=0)
        now = time.monotonic()
        with self.lock:
            for k in map(tuple, keys):
                self.cloud_mem[k] = now

    def obstacles(self):
        parts = [self.scan_pts]
        keep = float(self.p('cloud_memory_s'))
        if keep > 0 and self.pose is not None:
            now = time.monotonic()
            with self.lock:
                for k in [k for k, t in self.cloud_mem.items() if now - t > keep]:
                    del self.cloud_mem[k]
                g = np.array(list(self.cloud_mem.keys()), dtype=float) * 0.05
            if len(g):
                px, py, pyaw = self.pose
                c, s_ = math.cos(pyaw), math.sin(pyaw)
                dx, dy = g[:, 0] - px, g[:, 1] - py
                parts.append(np.stack([c * dx + s_ * dy, -s_ * dx + c * dy], 1))
        else:
            parts += list(self.cloud_pts.values())
        return np.concatenate(parts) if parts else np.zeros((0, 2))

    def on_image(self, m):
        ns = Time.from_msg(m.header.stamp).nanoseconds
        with self.lock:
            self.img_buf[ns] = m
            for k in sorted(self.img_buf)[:-40]:
                del self.img_buf[k]
        if (self.p('detector') != 'opencv' or self.K is None
                or time.monotonic() - self.last_detect < 0.1):
            return
        self.last_detect = time.monotonic()
        gray = self.bridge.imgmsg_to_cv2(m, 'mono8')
        found = detect_tags(gray, self.K, self.D, float(self.p('tag_size')),
                            tuple(int(i) for i in self.p('tag_ids')))
        if found:
            self.ingest(found, m)

    def on_apriltag(self, arr):
        """apriltag_ros detections -> (tvec, normal) in the camera frame via the tag_N TF."""
        if self.p('detector') == 'opencv' or self.K is None or not arr.detections:
            return
        stamp = Time.from_msg(arr.header.stamp)
        with self.lock:
            img = self.img_buf.get(stamp.nanoseconds)
            if img is None and self.img_buf:                  # nearest frame within 0.2 s
                k = min(self.img_buf, key=lambda t: abs(t - stamp.nanoseconds))
                img = self.img_buf[k] if abs(k - stamp.nanoseconds) < 2e8 else None
        if img is None:
            return
        ids = tuple(int(i) for i in self.p('tag_ids'))
        found = {}
        for d in arr.detections:
            if int(d.id) not in ids or d.hamming != 0:
                continue
            try:
                tf = self.tf_buffer.lookup_transform(img.header.frame_id,
                                                     f'{self.p("tag_frame_prefix")}{d.id}', stamp,
                                                     timeout=Duration(seconds=0.05))
            except tf2_ros.TransformException:
                continue
            t = tf.transform.translation
            tvec = np.array([t.x, t.y, t.z])
            normal = quat_to_matrix(tf.transform.rotation)[:, 2]
            if float(normal @ tvec) > 0:                      # point out of the face, at us
                normal = -normal
            found[int(d.id)] = (tvec, normal)
        if found:
            self.ingest(found, img)

    def ingest(self, found, m):
        """Shared by both detectors: depth range, odom position, memory."""
        if self.mode is None:
            return
        found = self.depth_correct(found, m)
        if self.mode == 'imu':
            T = self.to_base(m.header.frame_id)
            pz = self.pose_at(Time.from_msg(m.header.stamp).nanoseconds)
            if T is None or pz is None:
                return
            c, s_ = math.cos(pz[2]), math.sin(pz[2])
            Rw = np.array([[c, -s_, 0.0], [s_, c, 0.0], [0.0, 0.0, 1.0]])
            R = Rw @ T[0]
            cam = Rw @ T[1] + np.array([pz[0], pz[1], 0.0])
        else:
            try:
                tf = self.tf_buffer.lookup_transform(self.p('odom_frame'), m.header.frame_id,
                                                     Time.from_msg(m.header.stamp),
                                                     timeout=Duration(seconds=0.1))
            except tf2_ros.TransformException:
                return
            R = quat_to_matrix(tf.transform.rotation)
            t = tf.transform.translation
            cam = np.array([t.x, t.y, t.z])
        now = time.monotonic()
        for tag_id, (tvec, normal) in found.items():
            pos = R @ np.asarray(tvec) + cam
            n = R @ np.asarray(normal)
            rng = float(np.linalg.norm(tvec))
            facing = math.atan2(n[1], n[0])
            with self.lock:
                first = tag_id not in self.memory
                prev = self.live.get(tag_id)
                # while turning fast the camera image and the pose disagree (tens of degrees in
                # the sim): keep the last still position, only the camera-relative data updates
                lim = float(self.p('record_max_yaw_rate_imu' if self.mode == 'imu'
                                   else 'record_max_yaw_rate'))
                still = abs(self.yaw_rate) <= lim
                if still or prev is None:
                    xy = (pos[0], pos[1], facing)
                else:
                    xy = (prev['x'], prev['y'], prev['facing'])
                self.live[tag_id] = dict(t=now, x=xy[0], y=xy[1], facing=xy[2], rng=rng, img=m,
                                         tvec=np.asarray(tvec, float), normal=np.asarray(normal, float))
                if not still:
                    continue
                calm = abs(self.yaw_rate) <= float(self.p('record_max_yaw_rate'))
                lst = self.samples.setdefault(tag_id, [])
                lst.append((pos[0], pos[1], facing, rng, 1.0 if calm else 0.0))
                del lst[:-100]
                a = np.array(lst)
                if a[:, 4].any():
                    a = a[a[:, 4] > 0]                        # sightings taken while still win
                a = a[a[:, 3] <= a[:, 3].min() + 0.5]        # closest sightings only
                self.memory[tag_id] = dict(
                    x=float(np.median(a[:, 0])), y=float(np.median(a[:, 1])),
                    facing=math.atan2(float(np.median(np.sin(a[:, 2]))),
                                      float(np.median(np.cos(a[:, 2])))),
                    closest=float(a[:, 3].min()))
            if first:
                mem = self.memory[tag_id]
                frame = 'gyro-odom' if self.mode == 'imu' else self.p('odom_frame')
                px, py, pyaw = self.pose
                self.get_logger().info(f'Tag {tag_id} seen at {rng:.1f} m -> stored at '
                                       f'({mem["x"]:.2f}, {mem["y"]:.2f}) in {frame} '
                                       f'(robot at {px:.2f},{py:.2f},{math.degrees(pyaw):.0f} deg).')

    def depth_correct(self, found, img):
        d = self.last_depth
        if d is None or d.encoding not in ('16UC1', 'mono16'):
            return found
        if abs((Time.from_msg(d.header.stamp) - Time.from_msg(img.header.stamp)).nanoseconds) > 4e8:
            return found
        depth = np.frombuffer(bytes(d.data), dtype=np.uint16).reshape(d.height, d.width)
        sx, sy = d.width / float(img.width), d.height / float(img.height)
        out = {}
        for i, (tvec, n) in found.items():
            tvec = np.asarray(tvec, dtype=float)
            if np.linalg.norm(tvec) < float(self.p('depth_min_range')) or tvec[2] <= 0:
                out[i] = (tvec, n)
                continue
            u = self.K[0, 0] * tvec[0] / tvec[2] + self.K[0, 2]
            v = self.K[1, 1] * tvec[1] / tvec[2] + self.K[1, 2]
            cu, cv_ = int(round(u * sx)), int(round(v * sy))
            w = depth[max(cv_ - 3, 0):cv_ + 4, max(cu - 3, 0):cu + 4].astype(float) * 0.001
            w = w[(w > 0.3) & (w < 8.0)]
            out[i] = (tvec * (float(np.median(w)) / tvec[2]), n) \
                if (w.size >= 10 and np.std(w) < 0.08) else (tvec, n)
        return out

    def visible(self, tag, max_age=1.0):
        with self.lock:
            s = self.live.get(tag)
        return s if s is not None and time.monotonic() - s['t'] <= max_age else None

    # ============================================================== motion
    def good_enough(self, tag, max_age=0.5):
        """True if a fresh sighting already meets the visit rule with margin."""
        s = self.visible(tag, max_age)
        if s is None:
            return False
        tvec, n = s['tvec'], s['normal']
        cam = -tvec                                           # camera seen from the tag
        along = float(cam @ n)                                # out along the face normal
        lateral = float(np.linalg.norm(cam - along * n))
        off = math.degrees(math.acos(max(-1.0, min(1.0, -float(n[2])))))
        lo, hi = [float(v) for v in self.p('accept_cam_range')]
        return (lo <= along <= hi and off <= float(self.p('accept_angle_deg'))
                and lateral <= float(self.p('accept_lateral')))

    def send(self, v, w):
        c = Twist()
        c.linear.x, c.angular.z = float(v), float(w)
        self.last_cmd = c
        if self.p('stamped'):
            st = TwistStamped()
            st.header.stamp = self.get_clock().now().to_msg()
            st.header.frame_id = self.p('stamp_frame')
            st.twist = c
            c = st
        self.cmd_pub.publish(c)

    def stop(self):
        self.send(0.0, 0.0)

    def in_robot(self, x, y):
        px, py, pyaw = self.pose
        c, s = math.cos(pyaw), math.sin(pyaw)
        return c * (x - px) + s * (y - py), -s * (x - px) + c * (y - py)

    def apf_cmd(self, gx, gy, exclude=None, slow_radius=0.6, rep_scale=1.0):
        """One potential-field step towards odom point (gx, gy). exclude: odom point whose
        surroundings must not repel (the tag being approached and its post)."""
        rx, ry = self.in_robot(gx, gy)
        dist = math.hypot(rx, ry)
        # constant pull (speed is reduced near the goal instead), so walls beside a tag
        # cannot hold the robot short of the visit pose
        att = np.array([rx, ry]) / max(dist, 1e-6) * float(self.p('attractive_gain'))
        pts = self.obstacles()
        if exclude is not None and len(pts):
            ex, ey = self.in_robot(*exclude)
            pts = pts[np.hypot(pts[:, 0] - ex, pts[:, 1] - ey) > 0.45]
        rep = np.zeros(2)
        front_clear = 9.0
        if len(pts):
            ahead = (pts[:, 0] > 0) & (np.abs(pts[:, 1]) < 0.27)
            if ahead.any():
                front_clear = float(pts[ahead, 0].min()) - 0.21
            # repulsion from the closest point per 10 deg sector only: summing every point
            # made the push scale with point density (lidar + camera), not with geometry
            ang = np.floor((np.arctan2(pts[:, 1], pts[:, 0]) + math.pi) / math.radians(10)).astype(int)
            rr = np.hypot(pts[:, 0], pts[:, 1])
            order = np.lexsort((rr, ang))
            first = np.ones(len(order), bool)
            first[1:] = ang[order][1:] != ang[order][:-1]
            pts = pts[order[first]]
            r = np.hypot(pts[:, 0], pts[:, 1])
            d = r - float(self.p('robot_radius'))
            d0 = float(self.p('influence_distance'))
            m = (d > 0.02) & (d < d0)
            if m.any():
                mag = rep_scale * float(self.p('repulsive_gain')) * (1.0 / d[m] - 1.0 / d0) / d[m] ** 2
                rep = -(pts[m] / r[m, None] * mag[:, None]).sum(0)
        f = att + rep
        head = math.atan2(f[1], f[0])
        if dist < 0.3 and abs(head) > math.radians(110):
            # overshot a little: back into place instead of turning round
            back = wrap(head - math.pi)
            w = float(np.clip(float(self.p('heading_gain')) * back,
                              -float(self.p('max_angular_z')), float(self.p('max_angular_z'))))
            v = -min(0.1, dist) * max(0.0, math.cos(back))
            return v, w, dist
        # near the goal turn gently: at full rate the robot overshoots a goal beside it and
        # dithers left/right instead of stepping over
        wmax = float(self.p('max_angular_z'))
        if dist < 0.4:
            wmax = min(wmax, max(0.3, 1.5 * dist))
        w = float(np.clip(float(self.p('heading_gain')) * head, -wmax, wmax))
        v = float(self.p('max_linear_x')) * max(0.0, math.cos(head)) ** 2 * min(1.0, dist / slow_radius)
        if abs(head) > math.radians(70):
            v = 0.0                                           # turn first
        if front_clear < float(self.p('front_stop')):
            v = 0.0                                           # hard guard
        elif front_clear < 0.5:
            v *= front_clear / 0.5
        self.dbg = (gx, gy, dist, v, w, front_clear, math.degrees(head))
        return v, w, dist

    def drive_to(self, gx, gy, tol, timeout, tag=None, exclude=None, stop_when_visible=None,
                 rep_scale=1.0, good_for=None, detour=True):
        """Potential-field go-to-goal with trap recovery. Returns 'arrived', 'visible',
        'good' (good_for tag already photographable), 'timeout' or 'stopped'."""
        end = time.monotonic() + timeout
        # progress towards (roughly) this goal, kept across the short calls of approach()
        pg = self.progress
        if pg is None or math.hypot(pg[0] - gx, pg[1] - gy) > 0.5:
            self.progress = pg = [gx, gy, math.hypot(self.pose[0] - gx, self.pose[1] - gy),
                                  time.monotonic()]
        trapped_since = None
        moved_ref = self.pose
        while rclpy.ok() and self.referee.running and time.monotonic() < end:
            if stop_when_visible is not None and self.visible(stop_when_visible, 0.5):
                self.stop()
                return 'visible'
            if good_for is not None and self.good_enough(good_for, 0.3):
                self.stop()
                return 'good'
            v, w, dist = self.apf_cmd(gx, gy, exclude=exclude, rep_scale=rep_scale)
            if dist <= tol:
                self.stop()
                return 'arrived'
            self.send(v, w)
            # no progress (potential-field local minimum: turning back and forth in front of
            # an obstacle) -> detour through the open direction nearest the goal
            if dist < pg[2] - 0.15:
                pg[2], pg[3] = dist, time.monotonic()
            elif (detour and dist > 0.4
                  and time.monotonic() - pg[3] > float(self.p('progress_time'))):
                self.detour(gx, gy)
                pg[2], pg[3] = math.hypot(self.pose[0] - gx, self.pose[1] - gy), time.monotonic()
                moved_ref, trapped_since = self.pose, None
                continue
            # trapped: asked to move but not moving (local minimum / blocked)
            moved = math.hypot(self.pose[0] - moved_ref[0], self.pose[1] - moved_ref[1])
            if moved > 0.08 or abs(wrap(self.pose[2] - moved_ref[2])) > 0.3:
                moved_ref, trapped_since = self.pose, None
            elif trapped_since is None:
                trapped_since = time.monotonic()
            elif time.monotonic() - trapped_since > float(self.p('stuck_time')):
                self.recover()
                moved_ref, trapped_since = self.pose, None
            time.sleep(0.1)
        self.stop()
        return 'timeout' if self.referee.running else 'stopped'

    def open_directions(self, step=30):
        """[(angle rad in robot frame, free m)] for a 0.7 m wide corridor."""
        pts = self.obstacles()
        out = []
        for a in np.radians(np.arange(-180, 180, step)):
            dirv = np.array([math.cos(a), math.sin(a)])
            free = 4.0
            if len(pts):
                along = pts @ dirv
                lateral = np.abs(pts @ np.array([-dirv[1], dirv[0]]))
                blk = along[(along > 0) & (lateral < 0.35)]
                free = float(blk.min()) if len(blk) else 4.0
            out.append((float(a), free))
        return out

    def detour(self, gx, gy):
        """Side-step a blockage: drive ~1 m through the open direction closest to the goal."""
        prev = self.status
        self.status = 'DETOUR'
        rx, ry = self.in_robot(gx, gy)
        goal_a = math.atan2(ry, rx)
        best, best_score = None, -1e9
        for a, free in self.open_directions():
            if free < 0.9:
                continue
            score = min(free, 2.0) - 1.2 * abs(wrap(a - goal_a)) / math.pi
            if score > best_score:
                best, best_score, best_free = a, score, free
        if best is None:
            self.get_logger().warn('No progress and no open direction: recovering.')
            self.recover()
        else:
            step = min(1.0, best_free - 0.5)
            px, py, pyaw = self.pose
            self.get_logger().info(f'No progress for {self.p("progress_time")} s: detour '
                                   f'{math.degrees(best):.0f} deg for {step:.1f} m.')
            self.drive_to(px + step * math.cos(pyaw + best), py + step * math.sin(pyaw + best),
                          0.2, 8.0, detour=False)
        self.progress = None
        self.status = prev

    def recover(self):
        self.status = 'RECOVER'
        self.get_logger().warn('Trapped: backing up and turning towards open space.')
        self.reverse(0.3)
        pts = self.obstacles()
        left = pts[(pts[:, 1] > 0) & (np.hypot(pts[:, 0], pts[:, 1]) < 1.2)] if len(pts) else pts
        right = pts[(pts[:, 1] < 0) & (np.hypot(pts[:, 0], pts[:, 1]) < 1.2)] if len(pts) else pts
        self.turn_by(math.radians(60) * (1 if len(left) < len(right) else -1))

    def reverse(self, dist, speed=0.15):
        start = self.pose
        end = time.monotonic() + dist / speed + 2.0
        while rclpy.ok() and self.referee.running and time.monotonic() < end:
            if math.hypot(self.pose[0] - start[0], self.pose[1] - start[1]) >= dist:
                break
            pts = self.obstacles()
            behind = pts[(pts[:, 0] < 0) & (np.abs(pts[:, 1]) < 0.27)] if len(pts) else pts
            if len(behind) and (-behind[:, 0]).min() - 0.30 < 0.10:
                break                                         # rear guard
            self.send(-speed, 0.0)
            time.sleep(0.05)
        self.stop()

    def turn_by(self, angle, speed=None):
        speed = speed or float(self.p('max_angular_z'))
        target = wrap(self.pose[2] + angle)
        end = time.monotonic() + abs(angle) / max(speed * 0.5, 0.1) + 3.0
        while rclpy.ok() and self.referee.running and time.monotonic() < end:
            err = wrap(target - self.pose[2])
            if abs(err) < 0.05:
                break
            self.send(0.0, math.copysign(min(speed, max(0.2, 1.5 * abs(err))), err))
            time.sleep(0.05)
        self.stop()

    def sweep(self, tag):
        """360 deg look-around in steps (turn sweep_step_deg, hold still sweep_pause so the
        tags in view are stored with a clean pose); stops early as soon as `tag` is visible."""
        self.status = 'SWEEP'
        step = math.radians(float(self.p('sweep_step_deg')))
        speed = max(float(self.p('search_spin_speed')), 0.5)
        for _ in range(int(math.ceil(2 * math.pi / step))):
            if not (rclpy.ok() and self.referee.running) or self.visible(tag, 0.5) \
                    or tag in self.memory:
                break
            self.turn_by(step, speed=speed)
            end = time.monotonic() + float(self.p('sweep_pause'))
            while time.monotonic() < end and not self.visible(tag, 0.3):
                time.sleep(0.05)
        self.stop()

    def wander(self, tag):
        """Drive towards the most open direction for one step (a tag ahead stops it)."""
        self.status = 'WANDER'
        pts = self.obstacles()
        px, py, pyaw = self.pose
        crumbs = np.array(self.crumbs[-300:]) if self.crumbs else np.zeros((0, 2))
        best, best_free, best_room = 0.0, -1e9, 0.8
        for a in np.radians(np.arange(-150, 181, 30)):
            dirv = np.array([math.cos(a), math.sin(a)])
            if len(pts):
                along = pts @ dirv
                lateral = np.abs(pts @ np.array([-dirv[1], dirv[0]]))
                blk = along[(along > 0) & (lateral < 0.35)]
                free = float(blk.min()) if len(blk) else 4.0
            else:
                free = 4.0
            score = free - 0.3 * abs(a) / math.pi             # mild preference for ahead
            if len(crumbs) and free > 0.6:
                # novelty: how far the step's end point is from everywhere we have been
                step = min(float(self.p('wander_distance')), free - 0.5)
                ex, ey = px + step * math.cos(pyaw + a), py + step * math.sin(pyaw + a)
                near = float(np.hypot(crumbs[:, 0] - ex, crumbs[:, 1] - ey).min())
                score += float(self.p('novelty_gain')) * min(near, 1.5)
            if score > best_free:
                best, best_free, best_room = a, score, free
        step = min(float(self.p('wander_distance')), max(0.3, best_room - 0.5))
        gx, gy = px + step * math.cos(pyaw + best), py + step * math.sin(pyaw + best)
        self.drive_to(gx, gy, 0.2, float(self.p('wander_time')), stop_when_visible=tag)

    # ============================================================== per-tag
    def approach(self, tag):
        """Live-camera approach to the visit pose, then square up. True when in pose."""
        standoff = float(self.p('standoff'))
        # APPROACH: a staging point out along the normal (loose tolerance, time-capped; it only
        # has to bring the tag close). CLOSE_IN: the visit pose itself.
        for stage, extra, tol, limit in (
                ('APPROACH', float(self.p('approach_extra')), 0.2, 15.0),
                ('CLOSE_IN', 0.0, float(self.p('pos_tolerance')), 25.0)):
            self.status = stage
            end = time.monotonic() + limit
            while rclpy.ok() and self.referee.running and time.monotonic() < end:
                s = self.visible(tag, 1.0)
                mem = self.memory.get(tag)
                # far away the single live sighting's facing is noisy (the goal would swing
                # sideways every second): use the memory (median of the closest sightings)
                # unless the live sighting is close
                src = s if (s is not None and (mem is None or s['rng'] < 1.5)) else mem
                if src is None:
                    return False
                d = standoff + extra
                gx, gy = src['x'] + d * math.cos(src['facing']), src['y'] + d * math.sin(src['facing'])
                r = self.drive_to(gx, gy, tol, timeout=1.0, exclude=(src['x'], src['y']),
                                  rep_scale=1.0 if extra else float(self.p('close_in_repulsion')),
                                  good_for=tag)
                if r == 'good':
                    self.get_logger().info(f'Tag {tag}: pose is within the rules; taking the picture.')
                    return True
                if r == 'arrived':
                    break
            else:
                if stage == 'CLOSE_IN':
                    return False
                self.get_logger().info(f'Tag {tag}: staging point not reached in {limit:.0f} s; '
                                       'closing in from here.')
        # square up: face the tag
        self.status = 'ALIGN'
        for _ in range(4):
            if self.good_enough(tag, 0.5):
                return True
            time.sleep(0.3)                                   # a fresh frame after stopping
            g = self.geometry(tag, 0.6)
            if g is None:
                src = self.memory.get(tag)                    # not in view: memory heading
                if src is None:
                    return False
                self.turn_by(wrap(src['facing'] + math.pi - self.pose[2]), speed=0.4)
                continue
            if abs(g[2]) >= float(self.p('yaw_tolerance_deg')):
                self.turn_by(-math.radians(g[2]), speed=0.3)  # live camera heading error
                continue
            # heading fine: trim the range straight along the heading (camera-measured)
            err = g[0] - self.cam_target(tag)
            if abs(err) <= 0.03:
                return True
            self.straight(err)
        return True

    def cam_target(self, tag):
        """Camera -> tag-plane distance when the robot centre is at the standoff."""
        s = self.visible(tag, 2.0)
        T = self.to_base(s['img'].header.frame_id) if s is not None else None
        off = -float(T[1][0]) if T is not None else 0.05     # camera behind the centre: +
        return float(self.p('standoff')) + off

    def straight(self, dist, speed=0.08):
        """Drive straight by dist m (+ forward) with the front/rear guards."""
        start = self.pose
        end = time.monotonic() + abs(dist) / speed + 2.0
        while rclpy.ok() and self.referee.running and time.monotonic() < end:
            if math.hypot(self.pose[0] - start[0], self.pose[1] - start[1]) >= abs(dist) - 0.005:
                break
            pts = self.obstacles()
            if len(pts):
                band = np.abs(pts[:, 1]) < 0.27
                if dist > 0 and (pts[band & (pts[:, 0] > 0), 0] - 0.21 < 0.08).any():
                    break
                if dist < 0 and (-pts[band & (pts[:, 0] < 0), 0] - 0.30 < 0.10).any():
                    break
            self.send(math.copysign(speed, dist), 0.0)
            time.sleep(0.03)
        self.stop()
        time.sleep(0.3)

    def geometry(self, tag, max_age=0.5):
        """(along m, lateral m, signed heading error deg; + = tag normal to the right)
        of the camera relative to the tag face, from a fresh sighting."""
        s = self.visible(tag, max_age)
        if s is None:
            return None
        tvec, n = s['tvec'], s['normal']
        cam = -tvec
        along = float(cam @ n)
        lateral = float(np.linalg.norm(cam - along * n))
        return along, lateral, math.degrees(math.atan2(-float(n[0]), -float(n[2])))

    def report(self, tag):
        self.status = 'REPORT'
        self.stop()
        time.sleep(0.4)
        after = time.monotonic()
        end = after + 3.0
        while rclpy.ok() and time.monotonic() < end:
            s = self.visible(tag, 0.5)
            if s is not None and s['t'] > after:
                along, lateral, off = self.geometry(tag, 0.5) or (0.0, 9.0, 99.0)
                self.get_logger().info(f'Tag {tag}: camera {along:.2f} m out, {lateral:.2f} m to the '
                                       f'side, {abs(off):.1f} deg off square-on.')
                lo, hi = [float(v) for v in self.p('accept_cam_range')]
                if not (lo - 0.05 <= along <= hi + 0.03 and abs(off) <= 10.0 and lateral <= 0.15):
                    self.get_logger().warn(f'Tag {tag}: outside the visit rule; not reporting, '
                                           're-approaching.')
                    return False
                if self.referee.report_tag(tag, s['img']):
                    hold_end = time.monotonic() + VISIT_HOLD_S + 0.2
                    while time.monotonic() < hold_end:
                        self.stop()
                        time.sleep(0.1)
                    self.reverse(0.4)
                    return True
                return False
            time.sleep(0.05)
        self.get_logger().warn(f'Tag {tag}: not in view at the visit pose; not reporting.')
        return False

    def do_tag(self, tag):
        log = self.get_logger()
        sweeps = 0
        while rclpy.ok() and self.referee.running:
            if self.visible(tag, 1.0):
                log.info(f'Tag {tag}: in view; approaching.')
                if self.approach(tag) and self.report(tag):
                    return True
                self.reverse(0.3)
                continue
            mem = self.memory.get(tag)
            if mem is not None:
                self.status = 'GOTO_MEMORY'
                d = float(self.p('standoff')) + 0.6
                gx, gy = mem['x'] + d * math.cos(mem['facing']), mem['y'] + d * math.sin(mem['facing'])
                log.info(f'Tag {tag}: going to its remembered spot ({gx:.2f}, {gy:.2f}).')
                r = self.drive_to(gx, gy, float(self.p('memory_reach')), 40.0,
                                  exclude=(mem['x'], mem['y']), stop_when_visible=tag)
                if r == 'visible':
                    continue
                # anti-drift: at the spot but not visible -> face it, then a slow sweep
                self.turn_by(wrap(math.atan2(mem['y'] - self.pose[1], mem['x'] - self.pose[0]) - self.pose[2]))
                if not self.visible(tag, 1.0):
                    self.sweep(tag)
                if not self.visible(tag, 1.0):
                    log.warn(f'Tag {tag}: not at its remembered spot; searching again.')
                    with self.lock:
                        self.memory.pop(tag, None)
                        self.samples.pop(tag, None)
                continue
            self.status = 'SEARCH'
            self.sweep(tag)
            sweeps += 1
            if not self.visible(tag, 1.0) and tag not in self.memory:
                self.wander(tag)
        return False

    def run(self):
        try:
            self.run_loop()
        except Exception:                                     # noqa: BLE001
            if rclpy.ok() and self.context.ok():
                raise                                         # a real error: show it
            # Ctrl-C mid-command: the node is being destroyed, nothing to report

    def run_loop(self):
        log = self.get_logger()
        while rclpy.ok() and (self.pose is None or self.K is None or self.mode is None):
            time.sleep(0.2)
        while rclpy.ok():
            while rclpy.ok() and not self.referee.running:
                time.sleep(0.1)
            order = list(self.referee.tag_order)
            log.info(f'Run started. Order {order}.')
            for tag in order:
                if not self.referee.running:
                    break
                if tag not in self.referee.reported:
                    self.do_tag(tag)
            self.stop()
            if self.referee.running and self.referee.remaining_tags:
                self.referee.finish(completed=False)
            self.status = 'DONE'
            log.info('Run done.')
            while rclpy.ok() and self.referee.running:
                time.sleep(0.1)

    def log_status(self):
        if self.referee.running:
            known = {k: f'({v["x"]:.1f},{v["y"]:.1f})' for k, v in sorted(self.memory.items())}
            px, py, pyaw = self.pose
            msg = (f'[{self.status}] pose ({px:.2f},{py:.2f},{math.degrees(pyaw):.0f}) '
                   f'known tags: {known or "none"}')
            if self.dbg is not None and self.status not in ('SWEEP', 'REPORT', 'WAIT'):
                gx, gy, dist, v, w, fc, head = self.dbg
                msg += (f' | goal ({gx:.2f},{gy:.2f}) {dist:.2f} m, head {head:.0f} deg, '
                        f'cmd v={v:.2f} w={w:.2f}, front {fc:.2f} m')
            self.get_logger().info(msg)


def main(args=None):
    rclpy.init(args=args)
    node = MinimalTagTracker()
    ex = MultiThreadedExecutor()
    ex.add_node(node)
    try:
        ex.spin()
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
