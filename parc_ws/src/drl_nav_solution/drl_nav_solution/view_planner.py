"""Where to look next for tags that have not been found yet. Plain numpy, used by
both the ROS node and the 2D evaluator.

No obstacle map is built for driving. The planner keeps:
  * tag hypotheses - every place a tag could still be, from the rules: wall tags
    on the 4 walls (>= 1 m from corners) facing inward; free-standing tags in the
    interior (>= 1.4 m from walls) facing any of 8 directions; nothing within
    2.2 m of a tag already found or 1.8 m of the start;
  * a coarse 0.25 m record of where obstacles were seen, only so a viewpoint is
    not chosen inside furniture.

A hypothesis is cleared when the camera has had it in view (range, field of view
and viewing angle conservative against the real detector) with a clear line of
sight, or when an obstacle was seen inside the 1.5 m x 1.2 m area that the
arena generator keeps clear in front of every tag. The next viewpoint maximises
(weight of hypotheses a full turn there would check) / (travel + turn time).

Frame: the planner works in the map frame of the run, whose origin is the start
pose (x forward, y left). The arena in that frame is given by `bounds`.
"""

import math

import numpy as np

# Arena in the start-pose frame: 7 m x 6 m, start 1 m in front of the back wall,
# centred. x from -1 to 5, y from -3.5 to 3.5.
DEFAULT_BOUNDS = (-1.0, 5.0, -3.5, 3.5)


class ViewPlanner:
    def __init__(self, bounds=DEFAULT_BOUNDS, cam_range=2.8, cam_half_fov=math.radians(38),
                 max_off_face=math.radians(55), free_off_face=math.radians(33), wall_margin=1.0, free_margin=1.4,
                 tag_separation=2.2, start_separation=1.8, wall_weight=3.0, free_weight=1.0,
                 v_travel=0.35, spin_speed=0.9):
        self.xmin, self.xmax, self.ymin, self.ymax = bounds
        self.cam_range, self.cam_half_fov, self.max_off_face = cam_range, cam_half_fov, max_off_face
        self.tag_sep, self.v_travel, self.spin_speed = tag_separation, v_travel, spin_speed
        hx, hy, hf, hw = [], [], [], []
        # wall tags (0.03 m in front of the wall, facing inward)
        step = 0.3
        for wall_x, facing in ((self.xmin, 0.0), (self.xmax, math.pi)):
            for y in np.arange(self.ymin + wall_margin, self.ymax - wall_margin + 1e-6, step):
                hx.append(wall_x + (0.03 if facing == 0.0 else -0.03)); hy.append(y); hf.append(facing)
        for wall_y, facing in ((self.ymin, math.pi / 2), (self.ymax, -math.pi / 2)):
            for x in np.arange(self.xmin + wall_margin, self.xmax - wall_margin + 1e-6, step):
                hx.append(x); hy.append(wall_y + (0.03 if facing > 0 else -0.03)); hf.append(facing)
        n_wall = len(hx)
        for x in np.arange(self.xmin + free_margin, self.xmax - free_margin + 1e-6, 0.4):
            for y in np.arange(self.ymin + free_margin, self.ymax - free_margin + 1e-6, 0.4):
                for k in range(8):
                    hx.append(x); hy.append(y); hf.append(-math.pi + k * math.pi / 4)
        self.hx, self.hy, self.hf = np.array(hx), np.array(hy), np.array(hf)
        # Free-standing hypotheses face one of 8 directions; a real tag can be 22.5 deg
        # off its nearest one, so they are only cleared when seen closer to square-on.
        self.off_lim = np.full(len(hx), max_off_face)
        self.off_lim[n_wall:] = free_off_face
        w = np.zeros(len(hx))
        w[:n_wall] = wall_weight / n_wall
        w[n_wall:] = free_weight / (len(hx) - n_wall)
        self.w = w
        self.start_sep = start_separation
        self.found = []
        self.reset_hypotheses()
        # obstacle record for viewpoint choice
        self.res = 0.25
        self.nx = int(math.ceil((self.xmax - self.xmin) / self.res))
        self.ny = int(math.ceil((self.ymax - self.ymin) / self.res))
        self.blocked = np.zeros((self.nx, self.ny), np.int16)
        self.failed = []                      # viewpoints unreachable or already used

    def reset_hypotheses(self):
        self.open = np.hypot(self.hx, self.hy) >= self.start_sep
        for x, y in self.found:
            self.open &= np.hypot(self.hx - x, self.hy - y) >= self.tag_sep

    def restart_strict(self, factor=0.75):
        """Everything checked so far is doubted: re-open the hypotheses, shrink the
        assumed detection range and angles, and allow all viewpoints again. For when
        nothing is left to check but a tag is still missing (the detector is weaker
        than assumed, or a sighting was missed)."""
        self.cam_range *= factor
        self.off_lim *= factor
        self.cam_half_fov *= 0.9
        self.failed = []
        self.reset_hypotheses()

    # ------------------------------------------------------------- updates
    def tag_found(self, x, y):
        self.found.append((float(x), float(y)))
        self.open &= np.hypot(self.hx - x, self.hy - y) >= self.tag_sep

    def add_obstacles(self, ox, oy):
        """Obstacle points (map frame), e.g. the current scan."""
        i = ((np.asarray(ox) - self.xmin) / self.res).astype(int)
        j = ((np.asarray(oy) - self.ymin) / self.res).astype(int)
        ok = (i >= 0) & (i < self.nx) & (j >= 0) & (j < self.ny)
        np.add.at(self.blocked, (i[ok], j[ok]), 1)
        np.minimum(self.blocked, 1000, out=self.blocked)

    def observe(self, x, y, yaw, ray_fn):
        """Camera at (x, y, yaw). ray_fn(angles) -> free range along each world angle
        (inf where nothing was seen). Clears what a real tag there would have shown."""
        idx = np.flatnonzero(self.open)
        if not len(idx):
            return
        dx, dy = self.hx[idx] - x, self.hy[idx] - y
        d = np.hypot(dx, dy)
        bearing = np.arctan2(dy, dx)
        rel = np.abs(np.angle(np.exp(1j * (bearing - yaw))))
        off = np.abs(np.angle(np.exp(1j * (bearing + math.pi - self.hf[idx]))))
        cand = (d <= self.cam_range) & (rel <= self.cam_half_fov) & (off <= self.off_lim[idx])
        if not cand.any():
            return
        sel = idx[cand]
        free = ray_fn(bearing[cand])
        visible = free >= d[cand] - 0.15
        self.open[sel[visible]] = False
        # blocked line of sight: if the blocking point lies in the keep-out area in
        # front of the hypothesised tag, no tag can be there either
        bl = ~visible & np.isfinite(free)
        if bl.any():
            s = sel[bl]
            px = x + free[bl] * np.cos(bearing[cand][bl])
            py = y + free[bl] * np.sin(bearing[cand][bl])
            c, sn = np.cos(self.hf[s]), np.sin(self.hf[s])
            lx = (px - self.hx[s]) * c + (py - self.hy[s]) * sn
            ly = -(px - self.hx[s]) * sn + (py - self.hy[s]) * c
            inside = (lx > 0.1) & (lx < 1.4) & (np.abs(ly) < 0.55)
            self.open[s[inside]] = False

    # --------------------------------------------------------------- choice
    def remaining(self):
        return float(self.w[self.open].sum())

    def viewpoint_ok(self, x, y, clearance=0.45):
        r = int(math.ceil(clearance / self.res))
        i, j = int((x - self.xmin) / self.res), int((y - self.ymin) / self.res)
        sub = self.blocked[max(0, i - r):i + r + 1, max(0, j - r):j + r + 1]
        if sub.sum() > 0:
            return False
        return all(math.hypot(x - fx, y - fy) > 0.6 for fx, fy in self.failed)

    def used(self, x, y):
        """A full turn was made here (or it could not be reached): do not pick it again."""
        self.failed.append((float(x), float(y)))

    def spin_gain(self, vx, vy):
        """Weight a full turn at (vx, vy) would check (line of sight not known: assumed)."""
        idx = np.flatnonzero(self.open)
        dx, dy = self.hx[idx] - vx, self.hy[idx] - vy
        d = np.hypot(dx, dy)
        off = np.abs(np.angle(np.exp(1j * (np.arctan2(dy, dx) + math.pi - self.hf[idx]))))
        ok = (d <= self.cam_range) & (d >= 0.6) & (off <= self.off_lim[idx])
        return float(self.w[idx][ok].sum())

    def next_viewpoint(self, x, y, step=0.5, margin=0.6):
        """(vx, vy) in the map frame, or None when nothing worth checking is left."""
        if self.remaining() < 1e-6:
            return None
        best, best_score = None, 0.0
        spin_t = 2 * math.pi / self.spin_speed
        cands = [(vx, vy, 0.45)
                 for vx in np.arange(self.xmin + margin, self.xmax - margin + 1e-6, step)
                 for vy in np.arange(self.ymin + margin, self.ymax - margin + 1e-6, step)]
        # Points 1.2 m straight in front of open hypotheses: the generator keeps
        # 1.5 m x 1.2 m clear in front of every real tag, so if the hypothesis is
        # the tag, this point is free (smaller clearance check is enough).
        idx = np.flatnonzero(self.open)
        if len(idx) > 120:
            idx = idx[np.argsort(-self.w[idx])][:120]
        for i in idx:
            vx = self.hx[i] + 1.2 * math.cos(self.hf[i])
            vy = self.hy[i] + 1.2 * math.sin(self.hf[i])
            if self.xmin + 0.4 < vx < self.xmax - 0.4 and self.ymin + 0.4 < vy < self.ymax - 0.4:
                cands.append((vx, vy, 0.3))
        for vx, vy, clearance in cands:
            g = self.spin_gain(vx, vy)
            if g <= 0 or not self.viewpoint_ok(vx, vy, clearance):
                continue
            t = 1.3 * math.hypot(vx - x, vy - y) / self.v_travel + spin_t
            if g / t > best_score:
                best, best_score = (float(vx), float(vy)), g / t
        return best
