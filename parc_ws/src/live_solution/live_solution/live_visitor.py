"""No prior map: wheel odometry + live SLAM, camera-coverage exploration.

    ros2 launch live_solution live_solution.launch.py

Builds on explore_solution's ExploreVisitor (tag clues, approach, visit, referee) and
replaces its fixed sweep with exploration that works in ANY arena:

  * The lidar maps the whole arena within seconds (12 m range), but the camera only reads
    a tag within ~2.5 m. So the robot tracks what the CAMERA has looked at: a coverage
    grid where every camera frame marks the 90 deg wedge in front of it, 2.5 m deep.
  * Next goal = the nearest open floor (from the live SLAM map, clear of obstacles) that
    the camera has not covered yet. Drive there, spin (covers ~2.5 m around), repeat.
  * Clues still come first: the needed tag read even once (ID exact) -> go to it;
    a tag-like square seen repeatedly at camera height -> go and look.

Safety: scan spins always go through the collision monitor (no bypass: the lidar only
sees table bases, tabletops overhang them), and the search speed is limited.
"""

import math
import threading
import time

import numpy as np
import rclpy
from nav_msgs.msg import OccupancyGrid
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
import cv2
import tf2_ros
from rclpy.time import Time

from explore_solution.explore_visitor import ExploreVisitor

CELL = 0.25          # m, coverage grid resolution
HALF = 12.0          # m, coverage grid spans [-HALF, HALF] around the start


class LiveVisitor(ExploreVisitor):

    def __init__(self):
        super().__init__()
        self._ready = False
        self.declare_parameter('view_range', 2.5)          # m the camera can read a tag
        self.declare_parameter('view_fov_deg', 80.0)       # a bit under the 90 deg lens
        self.declare_parameter('goal_clearance', 0.45)     # m from obstacles for a goal
        self.declare_parameter('max_goals_per_tag', 12)
        self.set_parameters([rclpy.parameter.Parameter('spin_clearance', value=99.0)])  # never bypass
        n = int(2 * HALF / CELL)
        self.covered = np.zeros((n, n), bool)
        self.cov_lock = threading.Lock()
        self.last_cov = 0.0
        self.grid = None                                   # latest SLAM map
        self.failed_goals = []
        self.create_subscription(
            OccupancyGrid, '/map', self.on_map,
            QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                       durability=DurabilityPolicy.TRANSIENT_LOCAL))
        self.get_logger().info('Live mode: odometry + live SLAM; camera-coverage exploration.')
        self._ready = True

    # ------------------------------------------------------------- coverage
    def on_map(self, msg):
        self.grid = msg

    def on_image(self, msg):
        super().on_image(msg)
        if (not self._ready or not hasattr(self, 'covered') or not self.detecting
                or time.monotonic() - self.last_cov < 0.3):
            return
        self.last_cov = time.monotonic()
        try:
            tf = self.tf_buffer.lookup_transform(self.map_frame, msg.header.frame_id, Time())
        except tf2_ros.TransformException:
            return
        t = tf.transform.translation
        # camera optical z axis (viewing direction) in the map frame
        q = tf.transform.rotation
        x, y, z, w = q.x, q.y, q.z, q.w
        vx, vy = 2 * (x * z + y * w), 2 * (y * z - x * w)
        yaw = math.atan2(vy, vx)
        self.mark_view(t.x, t.y, yaw)

    def mark_view(self, cx, cy, yaw):
        rng = float(self.get_parameter('view_range').value)
        half = math.radians(float(self.get_parameter('view_fov_deg').value)) / 2
        n = self.covered.shape[0]
        i0, i1 = self.idx(cx - rng), self.idx(cx + rng)
        j0, j1 = self.idx(cy - rng), self.idx(cy + rng)
        ii, jj = np.mgrid[max(i0, 0):min(i1, n - 1) + 1, max(j0, 0):min(j1, n - 1) + 1]
        px, py = ii * CELL - HALF + CELL / 2, jj * CELL - HALF + CELL / 2
        dx, dy = px - cx, py - cy
        d = np.hypot(dx, dy)
        ang = np.abs(np.arctan2(np.sin(np.arctan2(dy, dx) - yaw), np.cos(np.arctan2(dy, dx) - yaw)))
        m = (d <= rng) & ((ang <= half) | (d < 0.6))
        with self.cov_lock:
            self.covered[ii[m], jj[m]] = True

    @staticmethod
    def idx(v):
        return int(math.floor((v + HALF) / CELL))

    def next_view_goal(self):
        """Nearest open, reachable-looking floor the camera has not covered yet."""
        g = self.grid
        me = self.pose2d(self.map_frame)
        if g is None or me is None:
            return None
        info = g.info
        a = np.array(g.data, dtype=np.int16).reshape(info.height, info.width)
        free = (a == 0).astype(np.uint8)
        blocked = ((a > 50) | (a < 0)).astype(np.uint8)
        # distance (m) from each free cell to the nearest obstacle/unknown
        dist = cv2.distanceTransform(1 - blocked, cv2.DIST_L2, 3) * info.resolution
        clear = (free == 1) & (dist >= float(self.get_parameter('goal_clearance').value))
        rr, cc = np.nonzero(clear[::5, ::5])               # sample every 5 cells (~0.25 m)
        if len(rr) == 0:
            return None
        xs = info.origin.position.x + (cc * 5 + 0.5) * info.resolution
        ys = info.origin.position.y + (rr * 5 + 0.5) * info.resolution
        with self.cov_lock:
            ci = np.clip(((xs + HALF) / CELL).astype(int), 0, self.covered.shape[0] - 1)
            cj = np.clip(((ys + HALF) / CELL).astype(int), 0, self.covered.shape[0] - 1)
            unseen = ~self.covered[ci, cj]
        xs, ys = xs[unseen], ys[unseen]
        if len(xs) == 0:
            return None
        ok = np.ones(len(xs), bool)
        for fx, fy in self.failed_goals:
            ok &= np.hypot(xs - fx, ys - fy) > 0.7
        xs, ys = xs[ok], ys[ok]
        if len(xs) == 0:
            return None
        d = np.hypot(xs - me[0], ys - me[1])
        d = np.where(d < 0.8, d + 5.0, d)                  # not right where we stand
        k = int(np.argmin(d))
        return float(xs[k]), float(ys[k]), int(len(xs))

    def coverage_left(self):
        with self.cov_lock:
            return int(self.covered.sum())

    # --------------------------------------------------------------- search
    def explore_until_known(self, tag):
        """Find `tag`: clues first (read once / tag-like squares), else camera coverage."""
        log = self.get_logger()
        self.current_target = tag
        self.set_detecting(True)
        tries_hint, cands_checked, goals, resets = 0, 0, 0, 0
        max_c = int(self.get_parameter('max_candidates_per_tag').value)
        max_goals = int(self.get_parameter('max_goals_per_tag').value)
        try:
            while rclpy.ok() and self.referee.running and not self.known(tag):
                hint = self.hints.get(tag)
                if hint is not None and tries_hint < 2:
                    tries_hint += 1
                    log.info(f'Tag {tag}: read once from {hint[2]:.1f} m; heading there to confirm it.')
                    self.approach_point(hint[0], hint[1], keep=1.3)
                    continue
                cand = self.next_candidate() if cands_checked < max_c else None
                if cand is not None:
                    cands_checked += 1
                    cand['done'] = True
                    log.info(f'Looking for tag {tag}: checking a tag-like square near '
                             f'({cand["x"]:.1f}, {cand["y"]:.1f}) (seen {cand["n"]}x).')
                    self.approach_point(cand['x'], cand['y'], keep=1.5)
                    continue
                if goals >= max_goals:
                    break
                goal = self.next_view_goal()
                if goal is None:
                    if resets == 0:                        # everything looked at once: look again
                        resets += 1
                        log.warn(f'Tag {tag}: whole map covered without seeing it; looking again.')
                        with self.cov_lock:
                            self.covered[:] = False
                        self.failed_goals.clear()
                        continue
                    break
                gx, gy, left = goal
                goals += 1
                log.info(f'Looking for tag {tag}: unseen area at ({gx:.1f}, {gy:.1f}) '
                         f'[{left} unseen spots left]. Known so far: {sorted(self.tags)}')
                before = self.pose2d(self.map_frame)
                self.goto(gx, gy)
                after = self.pose2d(self.map_frame)
                if before and after and math.hypot(after[0] - gx, after[1] - gy) > 0.8:
                    self.failed_goals.append((gx, gy))     # could not get there: try elsewhere
                if not self.known(tag) and self.referee.running and tag not in self.hints:
                    self.spin_scan()
        finally:
            self.current_target = None
        return self.known(tag)


def main(args=None):
    rclpy.init(args=args)
    node = LiveVisitor()
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
