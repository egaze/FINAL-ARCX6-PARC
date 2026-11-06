"""Map-free tag visits: view-planner exploration, driven by Nav2 or by a
PEEMEF-DARC policy (He et al., Sensors 2024).

    ros2 launch drl_nav_solution drl_solution.launch.py                 # Nav2 drives (default)
    ros2 launch drl_nav_solution drl_solution.launch.py driver:=drl     # learned policy drives

Same run logic as explore_solution.ExploreVisitor (spin, sweep, record tags, visit
in the referee's order, camera alignment, JPEG TagVisit, 3 s hold), but the two
driving legs no longer use Nav2:

  * navigate()  - to the approach region in front of a tag,
  * goto()      - to the next sweep point while looking for a tag,

are driven (with driver:=drl) by the learned policy straight from the merged scan: 24 range sectors
+ distance/angle to the goal + last command -> (v, w) at 10 Hz. No costmap and no
path planner. slam_toolbox still runs, only to keep map->odom free of drift so
recorded tag positions stay put.

If the policy makes no progress for `drl_stuck_s` the leg falls back to Nav2 (the
parent class's navigate()/goto()) unless `nav2_fallback` is false.

Exploration (`explorer:=view`, default) replaces the fixed sweep with
view_planner.ViewPlanner: it tracks where a tag could still be and picks the next
place to turn around at by value per second of travel. `explorer:=sweep` keeps
explore_solution's sweep. `arena_bounds` is the arena in the start-pose frame
(x forward, y left): the robot must be started at the official start pose.
"""

import math
import os
import threading
import time

import numpy as np
import rclpy
import tf2_ros
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Twist
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import LaserScan

from explore_solution.explore_visitor import ExploreVisitor
from drl_nav_solution import policy as P
from drl_nav_solution.view_planner import ViewPlanner


class DrlVisitor(ExploreVisitor):

    def __init__(self):
        super().__init__()
        default_policy = os.path.join(
            get_package_share_directory('drl_nav_solution'), 'weights', 'darc_policy.npz')
        self.declare_parameter('policy_file', default_policy)
        self.declare_parameter('policy_scan_topic', '/scan_merged')
        # Through the collision monitor by default (it slows the robot near obstacles);
        # '/cmd_vel' sends the policy straight to the wheels.
        self.declare_parameter('drl_cmd_topic', 'cmd_vel_smoothed')
        self.declare_parameter('drl_rate_hz', 10.0)
        self.declare_parameter('drl_stuck_s', 4.0)          # no 0.1 m progress -> stuck
        self.declare_parameter('drl_arrive', 0.25)          # m, sweep-point arrival
        # 'nav2': Nav2 drives every leg (safe default for the real robot);
        # 'drl': the PEEMEF-DARC policy drives, Nav2 only takes over when it is stuck.
        self.declare_parameter('driver', 'nav2')
        self.declare_parameter('nav2_fallback', True)
        self.declare_parameter('memory_s', P.MEMORY_S)      # s of remembered scan points
        self.declare_parameter('explorer', 'view')          # 'view' or 'sweep'
        self.declare_parameter('arena_bounds', [-1.0, 5.0, -3.5, 3.5])   # start-pose frame
        self.declare_parameter('view_range', 2.8)           # m the tag detector surely decodes at
        self.declare_parameter('view_half_fov_deg', 38.0)
        self.declare_parameter('view_off_face_deg', 55.0)
        p = lambda n: self.get_parameter(n).value  # noqa: E731

        self.driver = str(p('driver')).lower()
        if self.driver not in ('nav2', 'drl'):
            raise ValueError(f"driver must be 'nav2' or 'drl', not {self.driver!r}")
        self.policy = P.Policy(os.path.expanduser(p('policy_file'))) if self.driver == 'drl' else None
        self.memory = P.ObstacleMemory(horizon=float(p('memory_s')))
        self.scan_lock = threading.Lock()
        self.scan_pts = (np.zeros(0), np.zeros(0))          # base frame
        self.scan_stamp = None
        self.laser_tf = None                                # (x, y, yaw) laser in base
        self.last_cmd = (0.0, 0.0)
        self.drl_pub = self.create_publisher(Twist, p('drl_cmd_topic'), 10)
        self.create_subscription(LaserScan, p('policy_scan_topic'), self.on_policy_scan,
                                 qos_profile_sensor_data)
        self.stats_drl = {'legs': 0, 'fallbacks': 0}
        self.planner = ViewPlanner(
            bounds=tuple(float(v) for v in p('arena_bounds')),
            cam_range=float(p('view_range')),
            cam_half_fov=math.radians(float(p('view_half_fov_deg'))),
            max_off_face=math.radians(float(p('view_off_face_deg'))),
            spin_speed=float(p('spin_speed')), v_travel=0.35)
        self.planner_lock = threading.Lock()
        self.planner_found = set()
        self.planner_restarts = 0
        self.n_scans = 0
        self.create_timer(0.1, self.on_view_timer)
        self._drl_ready = True
        if self.driver == 'drl':
            self.get_logger().info(f'Driver: DRL policy from {p("policy_file")}; '
                                   f'Nav2 fallback {"on" if p("nav2_fallback") else "off"}.')
        else:
            self.get_logger().info('Driver: Nav2 (driver:=drl for the learned policy).')
        self.get_logger().info(f'Explorer: {p("explorer")}.')

    def run(self):
        # TagVisitor.__init__ starts this thread before this class has loaded the policy.
        while rclpy.ok() and not getattr(self, '_drl_ready', False):
            time.sleep(0.05)
        super().run()

    # -------------------------------------------------------------- sensing
    def on_policy_scan(self, msg):
        if self.laser_tf is None:
            try:
                tf = self.tf_buffer.lookup_transform(self.base_frame, msg.header.frame_id, Time())
            except tf2_ros.TransformException:
                return
            q = tf.transform.rotation
            self.laser_tf = (tf.transform.translation.x, tf.transform.translation.y,
                             math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z)))
        r = np.asarray(msg.ranges, float)
        a = msg.angle_min + np.arange(r.size) * msg.angle_increment
        ok = np.isfinite(r) & (r >= msg.range_min) & (r <= msg.range_max)
        r, a = r[ok], a[ok]
        lx, ly, lyaw = self.laser_tf
        bx = lx + r * np.cos(a + lyaw)
        by = ly + r * np.sin(a + lyaw)
        with self.scan_lock:
            self.scan_pts = (bx, by)
            self.scan_stamp = time.monotonic()
        # Nearby points go into the short-lived memory in the odom frame, exactly as
        # in training (sim2d.Robot.sense): table tops leave the cameras' view as the
        # robot turns, and returns closer than 0.3 m are dropped by the scan merger.
        me = self.pose2d(self.odom_frame)
        if me is None:
            return
        near = np.hypot(bx, by) <= P.MEMORY_RANGE
        c, s = math.cos(me[2]), math.sin(me[2])
        ox = me[0] + c * bx[near] - s * by[near]
        oy = me[1] + s * bx[near] + c * by[near]
        with self.scan_lock:
            self.memory.add(self.now().nanoseconds * 1e-9, ox, oy)   # sim time, like training

    # ---------------------------------------------------------- view planner
    def on_view_timer(self):
        """Clear tag hypotheses the camera has just had in view (only while the
        detector is really decoding frames) and record obstacles for viewpoint choice."""
        if not getattr(self, '_drl_ready', False) or not self.referee.running:
            return
        mp = self.pose2d(self.map_frame)
        with self.scan_lock:
            fresh = self.scan_stamp is not None and time.monotonic() - self.scan_stamp < 0.5
            bx, by = self.scan_pts
        if mp is None or not fresh:
            return
        x, y, yaw = mp
        ang = np.arctan2(by, bx) + yaw
        rng = np.hypot(bx, by)
        nb = 360
        bins = np.full(nb, np.inf)
        idx = (np.floor((ang + math.pi) / (2 * math.pi) * nb).astype(int)) % nb
        np.minimum.at(bins, idx, rng)

        def ray_fn(angles):
            k = (np.floor((np.asarray(angles) + math.pi) / (2 * math.pi) * nb).astype(int)) % nb
            return np.minimum(np.minimum(bins[k], bins[(k + 1) % nb]), bins[(k - 1) % nb])

        decoding = self.detecting and time.monotonic() - self.last_detect < 0.5
        c, s = math.cos(yaw), math.sin(yaw)
        with self.planner_lock:
            with self.rec_lock:
                found = {t: (v['x'], v['y']) for t, v in self.tags.items()}
            for t, (tx, ty) in found.items():
                if t not in self.planner_found:
                    self.planner_found.add(t)
                    self.planner.tag_found(tx, ty)
            if decoding:
                self.planner.observe(x, y, yaw, ray_fn)
            self.n_scans += 1
            if self.n_scans % 3 == 0:
                self.planner.add_obstacles(x + c * bx - s * by, y + s * bx + c * by)

    def explore_until_known(self, tag):
        if self.get_parameter('explorer').value != 'view':
            return super().explore_until_known(tag)
        log = self.get_logger()
        self.current_target = tag
        self.set_detecting(True)
        try:
            while rclpy.ok() and self.referee.running and not self.known(tag):
                me = self.pose2d(self.map_frame)
                if me is None:
                    time.sleep(0.1)
                    continue
                with self.planner_lock:
                    vp = self.planner.next_viewpoint(me[0], me[1])
                    if vp is None and self.planner_restarts < 2:
                        self.planner_restarts += 1
                        self.planner.restart_strict()
                        log.warn(f'Looking for tag {tag}: every place checked; checking again with '
                                 f'stricter detection limits (restart {self.planner_restarts}).')
                        vp = self.planner.next_viewpoint(me[0], me[1])
                    left = self.planner.remaining()
                if vp is None:
                    return False
                log.info(f'Looking for tag {tag}: viewpoint ({vp[0]:.1f}, {vp[1]:.1f}); '
                         f'unchecked weight {left:.2f}; known {sorted(self.tags)}')
                self.goto(*vp)
                with self.planner_lock:
                    self.planner.used(*vp)
                if not self.known(tag) and self.referee.running:
                    self.spin_scan()
                    me = self.pose2d(self.map_frame)
                    if me is not None:
                        with self.planner_lock:
                            self.planner.used(me[0], me[1])
        finally:
            self.current_target = None
        return self.known(tag)

    def policy_state(self, gx, gy):
        """28-number state for a goal (gx, gy) in the map frame, or None."""
        mp = self.pose2d(self.map_frame)
        od = self.pose2d(self.odom_frame)
        with self.scan_lock:
            fresh = self.scan_stamp is not None and time.monotonic() - self.scan_stamp < 0.5
            bx, by = self.scan_pts
            if od is not None:
                mx, my = self.memory.robot_frame(*od)
            else:
                mx = my = np.zeros(0)
        if mp is None or not fresh:
            return None, mp
        sectors = P.sectors_from_points(np.concatenate([bx, mx]), np.concatenate([by, my]))
        d = math.hypot(gx - mp[0], gy - mp[1])
        ang = P.wrap(math.atan2(gy - mp[1], gx - mp[0]) - mp[2])
        return P.build_state(sectors, d, ang, *self.last_cmd), mp

    # -------------------------------------------------------------- driving
    def drl_stop(self):
        self.last_cmd = (0.0, 0.0)
        self.drl_pub.publish(Twist())

    def drive_policy(self, gx, gy, timeout, done_fn):
        """Run the policy towards (gx, gy) [map] until done_fn(pose) returns a
        string (that string is returned), it is stuck ('stuck'), the time runs out
        or the run stops ('failed')."""
        rate = 1.0 / float(self.get_parameter('drl_rate_hz').value)
        stuck = Duration(seconds=float(self.get_parameter('drl_stuck_s').value))
        deadline = self.now() + Duration(seconds=timeout)
        wall_end = time.monotonic() + 3 * timeout
        best, best_at = None, self.now()
        self.stats_drl['legs'] += 1
        try:
            while rclpy.ok():
                if not self.referee.running or self.now() > deadline or time.monotonic() > wall_end:
                    return 'failed'
                state, me = self.policy_state(gx, gy)
                if state is None:
                    self.drl_stop()
                    time.sleep(rate)
                    continue
                result = done_fn(me)
                if result:
                    return result
                d = math.hypot(gx - me[0], gy - me[1])
                if best is None or d < best - 0.10:
                    best, best_at = d, self.now()
                elif self.now() - best_at > stuck:
                    return 'stuck'
                v, w = P.action_to_cmd(self.policy.act(state))
                self.last_cmd = (v, w)
                cmd = Twist()
                cmd.linear.x, cmd.angular.z = float(v), float(w)
                self.drl_pub.publish(cmd)
                self.sleep(rate)        # node (sim) time: the policy was trained at 10 Hz
            return 'failed'
        finally:
            self.drl_stop()

    def navigate(self, x, y, yaw, tag, radius, timeout):
        """Policy drive to the approach region of `tag` (same outcomes as the Nav2
        version: 'in_region', 'tag_in_view', 'stuck', 'failed')."""
        if self.driver == 'nav2':
            return super().navigate(x, y, yaw, tag, radius, timeout)
        log = self.get_logger()
        handoff = float(self.get_parameter('handoff_range').value)
        detect_range = float(self.get_parameter('detect_range').value)

        def done(me):
            t = self.tags.get(tag)
            if t is not None:
                self.set_detecting(math.hypot(t['x'] - me[0], t['y'] - me[1]) <= detect_range)
            if math.hypot(x - me[0], y - me[1]) <= radius:
                log.info(f'Tag {tag}: inside the approach region (policy); aligning with the camera.')
                return 'in_region'
            live = self.live_target(tag)
            if live is not None and live[1] <= handoff:
                log.info(f'Tag {tag}: in view at {live[1]:.2f} m (policy); aligning with the camera.')
                return 'tag_in_view'
            return None

        log.info(f'Tag {tag}: policy driving to ({x:.2f}, {y:.2f}).')
        outcome = self.drive_policy(x, y, timeout, done)
        if outcome == 'stuck' and self.get_parameter('nav2_fallback').value and self.referee.running:
            self.stats_drl['fallbacks'] += 1
            log.warn(f'Tag {tag}: policy stuck; Nav2 takes over this leg '
                     f'({self.stats_drl["fallbacks"]}/{self.stats_drl["legs"]} legs so far).')
            return super().navigate(x, y, yaw, tag, radius, timeout)
        return outcome

    def goto(self, x, y):
        """Policy drive to a sweep point; stops early when the target tag is found."""
        if self.driver == 'nav2':
            return super().goto(x, y)
        arrive = float(self.get_parameter('drl_arrive').value)
        timeout = float(self.get_parameter('waypoint_timeout_s').value)

        def done(me):
            if self.target_known():
                return 'found'
            if math.hypot(x - me[0], y - me[1]) <= arrive:
                return 'arrived'
            return None

        outcome = self.drive_policy(x, y, timeout, done)
        if outcome == 'stuck' and self.get_parameter('nav2_fallback').value and self.referee.running:
            self.stats_drl['fallbacks'] += 1
            self.get_logger().warn(f'Sweep point ({x:.1f}, {y:.1f}): policy stuck; Nav2 takes over.')
            super().goto(x, y)


def main(args=None):
    rclpy.init(args=args)
    node = DrlVisitor()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if rclpy.ok():
            node.stop()
            node.drl_stop()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
