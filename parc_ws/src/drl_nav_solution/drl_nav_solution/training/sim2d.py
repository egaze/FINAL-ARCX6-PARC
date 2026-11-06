"""Fast 2D simulator of the PARC randomised arena for training the policy.

Arenas come straight from parc_robot_bringup.world_generator (same seeds, same
obstacle shapes as the Gazebo world). The robot is the SITO-E footprint used by
Nav2 ([0.21, -0.30] x [-0.23, 0.23] around base_footprint), driven as a unicycle
with the robot's velocity and acceleration limits at 10 Hz.

Sensor model, to match /scan_merged on the robot:
  * lidar: 360 beams all round, but it only sees what reaches lidar height - a
    cafe table is its 4 cm centre column, a chair its legs;
  * depth cameras: 90 degrees ahead, see the full shapes (table tops, seats);
  * returns closer than 0.3 m are dropped (scan_merger range_min).
Camera points are kept for a few seconds in ObstacleMemory, as in the ROS node.
"""

import math
import os
import sys

import numpy as np

from drl_nav_solution import policy as P


def import_world_generator():
    try:
        from parc_robot_bringup import world_generator as wg
        return wg
    except ImportError:
        here = os.path.dirname(os.path.abspath(__file__))
        src = os.path.abspath(os.path.join(here, '..', '..', '..', 'parc_robot_bringup'))
        sys.path.insert(0, src)
        from parc_robot_bringup import world_generator as wg
        return wg


wg = import_world_generator()

FRONT, BACK, HALF_W = 0.21, -0.30, 0.23
DT = 0.1
ACC_V, ACC_W = 1.0, 2.0
RANGE_MIN, RANGE_MAX = 0.3, 8.0
LIDAR_ANGLES = np.linspace(-math.pi, math.pi, 360, endpoint=False)
CAM_ANGLES = np.linspace(-0.785, 0.785, 64)


def _footprint_samples(step=0.04):
    pts = []
    for x in np.arange(BACK, FRONT + 1e-9, step):
        pts += [(x, HALF_W), (x, -HALF_W)]
    for y in np.arange(-HALF_W, HALF_W + 1e-9, step):
        pts += [(FRONT, y), (BACK, y)]
    pts += [(x, 0.0) for x in np.arange(BACK, FRONT, 0.1)]
    return np.array(pts)


FOOTPRINT = _footprint_samples()


class ShapeSet:
    """Boxes and circles as arrays, for vectorised ray casting and distances."""

    def __init__(self, shapes):
        boxes = [s for s in shapes if isinstance(s, wg.Box)]
        circles = [s for s in shapes if isinstance(s, wg.Circle)]
        self.box = np.array([[b.cx, b.cy, b.hx, b.hy, b.yaw] for b in boxes]).reshape(-1, 5)
        self.cir = np.array([[c.cx, c.cy, c.r] for c in circles]).reshape(-1, 3)

    def raycast(self, ox, oy, angles):
        dx, dy = np.cos(angles), np.sin(angles)
        t = np.full(angles.shape, np.inf)
        # arena walls (inside a rectangle)
        with np.errstate(divide='ignore', invalid='ignore'):
            tx = np.where(dx > 0, (wg.XMAX - ox) / dx, np.where(dx < 0, (wg.XMIN - ox) / dx, np.inf))
            ty = np.where(dy > 0, (wg.YMAX - oy) / dy, np.where(dy < 0, (wg.YMIN - oy) / dy, np.inf))
        t = np.minimum(t, np.minimum(tx, ty))
        if len(self.box):
            cx, cy, hx, hy, yaw = (self.box[:, i][:, None] for i in range(5))
            c, s = np.cos(yaw), np.sin(yaw)
            lox = (ox - cx) * c + (oy - cy) * s
            loy = -(ox - cx) * s + (oy - cy) * c
            ldx = dx[None, :] * c + dy[None, :] * s
            ldy = -dx[None, :] * s + dy[None, :] * c
            ldx = np.where(np.abs(ldx) < 1e-12, 1e-12, ldx)
            ldy = np.where(np.abs(ldy) < 1e-12, 1e-12, ldy)
            t1x, t2x = (-hx - lox) / ldx, (hx - lox) / ldx
            t1y, t2y = (-hy - loy) / ldy, (hy - loy) / ldy
            tmin = np.maximum(np.minimum(t1x, t2x), np.minimum(t1y, t2y))
            tmax = np.minimum(np.maximum(t1x, t2x), np.maximum(t1y, t2y))
            hit = (tmax >= np.maximum(tmin, 0.0))
            tb = np.where(hit, np.maximum(tmin, 0.0), np.inf)
            t = np.minimum(t, tb.min(axis=0))
        if len(self.cir):
            cx, cy, r = (self.cir[:, i][:, None] for i in range(3))
            fx, fy = ox - cx, oy - cy
            b = fx * dx[None, :] + fy * dy[None, :]
            cc = fx * fx + fy * fy - r * r
            disc = b * b - cc
            tc = -b - np.sqrt(np.maximum(disc, 0.0))
            tc = np.where((disc >= 0) & (tc >= 0), tc, np.where(cc < 0, 0.0, np.inf))
            t = np.minimum(t, tc.min(axis=0))
        return t

    def min_distance(self, xs, ys):
        d = np.full(xs.shape, np.inf)
        for cx, cy, hx, hy, yaw in self.box:
            c, s = math.cos(yaw), math.sin(yaw)
            lx = (xs - cx) * c + (ys - cy) * s
            ly = -(xs - cx) * s + (ys - cy) * c
            qx, qy = np.abs(lx) - hx, np.abs(ly) - hy
            d = np.minimum(d, np.hypot(np.maximum(qx, 0), np.maximum(qy, 0))
                           + np.minimum(np.maximum(qx, qy), 0))
        for cx, cy, r in self.cir:
            d = np.minimum(d, np.hypot(xs - cx, ys - cy) - r)
        edge = np.minimum.reduce([xs - wg.XMIN, wg.XMAX - xs, ys - wg.YMIN, wg.YMAX - ys])
        return np.minimum(d, edge)


def lidar_view(obstacle):
    """What a lidar at ~0.2 m height sees of an obstacle (see module docstring)."""
    out = []
    if obstacle.kind == 'table_set':
        table = obstacle.shapes[0]
        out.append(wg.Circle(table.cx, table.cy, 0.03))
        for s in obstacle.shapes[1:]:
            if s.hy > 0.25:                       # seated visitor: legs/body, solid
                out.append(s)
            else:                                 # chair: four legs
                c, sn = math.cos(s.yaw), math.sin(s.yaw)
                for ox, oy in ((s.hx - 0.03, s.hy - 0.03), (-s.hx + 0.03, s.hy - 0.03),
                               (s.hx - 0.03, -s.hy + 0.03), (-s.hx + 0.03, -s.hy + 0.03)):
                    out.append(wg.Circle(s.cx + ox * c - oy * sn, s.cy + ox * sn + oy * c, 0.02))
    elif obstacle.kind == 'plant':
        s = obstacle.shapes[0]
        out.append(wg.Circle(s.cx, s.cy, 0.20))   # pot; the 0.33 m foliage is higher up
    else:
        out.extend(obstacle.shapes)
    return out


class Arena:
    def __init__(self, seed):
        self.seed = seed
        self.world = wg.generate(seed)
        signs = [t.sign_shape() for t in self.world.tags]
        full = signs + [s for o in self.world.obstacles for s in o.shapes]
        self.collide = ShapeSet(full)
        self.camera = self.collide
        self.lidar = ShapeSet(signs + [s for o in self.world.obstacles for s in lidar_view(o)])
        self.tags = {t.tag_id: t for t in self.world.tags}
        self._free = {}

    # ---- planning helpers (expert demonstrations / fallback only)
    def free_grid(self, clearance):
        if clearance not in self._free:
            g = wg.Grid()
            d = self.collide.min_distance(g.X, g.Y)
            self._free[clearance] = (g, d > clearance)
        return self._free[clearance]

    def plan(self, start, goal, clearance=0.36, fallbacks=(0.32, 0.28)):
        """Grid shortest path (list of (x, y)) or None. Falls back to smaller clearance."""
        for cl in (clearance, *fallbacks):
            g, free = self.free_grid(cl)
            s, e = g.cell(*start), g.cell(*goal)
            free = free.copy()
            free[s] = free[e] = True
            dist = g.distances_from(free, e)
            if not np.isfinite(dist[s]):
                continue
            path, cur = [], s
            rows, cols = free.shape
            while cur != e and len(path) < 5000:
                path.append((g.xs[cur[1]], g.ys[cur[0]]))
                best = None
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        r, c = cur[0] + dr, cur[1] + dc
                        if (dr or dc) and 0 <= r < rows and 0 <= c < cols:
                            v = dist[r, c] + math.hypot(dr, dc) * wg.GRID
                            if best is None or v < best[0]:
                                best = (v, (r, c))
                cur = best[1]
            path.append(goal)
            return path
        return None

    def clearance(self, x, y, yaw):
        """Smallest distance from the footprint outline to anything (<= 0: touching)."""
        c, s = math.cos(yaw), math.sin(yaw)
        px = x + FOOTPRINT[:, 0] * c - FOOTPRINT[:, 1] * s
        py = y + FOOTPRINT[:, 0] * s + FOOTPRINT[:, 1] * c
        return float(self.collide.min_distance(px, py).min())

    def pose_free(self, x, y, yaw, margin=0.0):
        return self.clearance(x, y, yaw) > margin

    def line_of_sight(self, x0, y0, x1, y1):
        ang = math.atan2(y1 - y0, x1 - x0)
        d = self.camera.raycast(x0, y0, np.array([ang]))[0]
        return d >= math.hypot(x1 - x0, y1 - y0) - 0.08


class Robot:
    """Kinematics + sensors + obstacle memory for one robot in an Arena."""

    def __init__(self, arena, x, y, yaw, noise=0.01, rng=None):
        self.arena = arena
        self.x, self.y, self.yaw = x, y, yaw
        self.v = self.w = 0.0
        self.t = 0.0
        self.noise = noise
        self.rng = rng or np.random.default_rng()
        self.memory = P.ObstacleMemory()
        self.crashed = False
        self.sense()

    def sense(self):
        a = self.arena
        lid = a.lidar.raycast(self.x, self.y, self.yaw + LIDAR_ANGLES)
        cam = a.camera.raycast(self.x, self.y, self.yaw + CAM_ANGLES)
        if self.noise:
            lid = lid + self.rng.normal(0, self.noise, lid.shape)
            cam = cam + self.rng.normal(0, 0.004, cam.shape) * cam ** 2
        lid_ok = (lid >= RANGE_MIN) & (lid <= RANGE_MAX)
        cam_ok = (cam >= RANGE_MIN) & (cam <= RANGE_MAX)
        r = np.concatenate([lid[lid_ok], cam[cam_ok]])
        ang = np.concatenate([LIDAR_ANGLES[lid_ok], CAM_ANGLES[cam_ok]])
        self.scan_x, self.scan_y = r * np.cos(ang), r * np.sin(ang)
        # All nearby points go into the short memory (world frame): keeps table tops
        # that left the cameras' view, and anything that came closer than the 0.3 m
        # range_min, in view of the policy. Lidar is thinned to every 2nd beam.
        mr = np.concatenate([lid[lid_ok][::2], cam[cam_ok]])
        ma = np.concatenate([LIDAR_ANGLES[lid_ok][::2], CAM_ANGLES[cam_ok]]) + self.yaw
        near = mr <= P.MEMORY_RANGE
        self.memory.add(self.t, self.x + mr[near] * np.cos(ma[near]),
                        self.y + mr[near] * np.sin(ma[near]))

    def sectors(self):
        mx, my = self.memory.robot_frame(self.x, self.y, self.yaw)
        return P.sectors_from_points(np.concatenate([self.scan_x, mx]),
                                     np.concatenate([self.scan_y, my]))

    def state(self, gx, gy):
        d = math.hypot(gx - self.x, gy - self.y)
        ang = P.wrap(math.atan2(gy - self.y, gx - self.x) - self.yaw)
        return P.build_state(self.sectors(), d, ang, self.v, self.w)

    def step(self, v_cmd, w_cmd, dt=DT, sense=True):
        """Apply a command for dt with acceleration limits. Sets self.crashed."""
        self.v += float(np.clip(v_cmd - self.v, -ACC_V * dt, ACC_V * dt))
        self.w += float(np.clip(w_cmd - self.w, -ACC_W * dt, ACC_W * dt))
        n = 2
        for _ in range(n):
            self.yaw = P.wrap(self.yaw + self.w * dt / n / 2)
            self.x += self.v * math.cos(self.yaw) * dt / n
            self.y += self.v * math.sin(self.yaw) * dt / n
            self.yaw = P.wrap(self.yaw + self.w * dt / n / 2)
        self.t += dt
        if not self.arena.pose_free(self.x, self.y, self.yaw):
            self.crashed = True
        if sense:
            self.sense()
