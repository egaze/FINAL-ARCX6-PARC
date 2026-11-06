"""Navigation episodes in randomised PARC arenas, with the reward and an expert.

An episode is one navigation leg the real run needs: from the start pose or from
just after a tag visit (backed out in front of a tag) or from anywhere, to the
approach point in front of another tag or to an exploration point.

Reward (same terms as the paper's turtlebot_turtlebot3_peemef_darc_env.py,
rescaled, and with the paper's 0.2 m/s speed cap removed because the run is
timed):
    progress towards the goal       +8 per metre
    time                            -0.03 per step
    laser term                      penalty when the closest sector < 0.5 m
    footprint clearance             penalty below 0.10 m (simulator knows it exactly)
    angular term                    -0.03 * |w|
    arrive (within `arrive` m)      +15, episode ends
    collision                       -15, episode ends
"""

import math

import numpy as np

from drl_nav_solution import policy as P
from drl_nav_solution.training import sim2d as S

APPROACH = 0.85          # m in front of a tag: where the camera alignment takes over


def approach_point(tag, d=APPROACH):
    return tag.x + d * math.cos(tag.facing), tag.y + d * math.sin(tag.facing)


class NavEnv:
    def __init__(self, seeds, rng, max_steps=450, arrive=0.25):
        self.seeds = list(seeds)
        self.rng = rng
        self.max_steps = max_steps
        self.arrive = arrive
        self.cache = {}

    def arena(self, seed):
        if seed not in self.cache:
            self.cache[seed] = S.Arena(seed)
        return self.cache[seed]

    def random_free_point(self, arena, clearance=0.45):
        g, free = arena.free_grid(clearance)
        cells = np.argwhere(free)
        r, c = cells[self.rng.integers(len(cells))]
        return float(g.xs[c]), float(g.ys[r])

    def sample_task(self, arena):
        tags = list(arena.tags.values())
        kind = self.rng.random()
        if kind < 0.25:
            sx, sy, syaw = S.wg.START
        elif kind < 0.65:
            t = tags[self.rng.integers(len(tags))]
            sx, sy = approach_point(t, 0.85)
            syaw = P.wrap(t.facing + math.pi + self.rng.normal(0, 0.3))
        else:
            sx, sy = self.random_free_point(arena)
            syaw = self.rng.uniform(-math.pi, math.pi)
        if self.rng.random() < 0.75:
            t = tags[self.rng.integers(len(tags))]
            gx, gy = approach_point(t)
        else:
            gx, gy = self.random_free_point(arena)
        return (sx, sy, syaw), (gx, gy)

    def reset(self, seed=None, task=None):
        for _ in range(50):
            self.seed = seed if seed is not None else self.seeds[self.rng.integers(len(self.seeds))]
            a = self.arena(self.seed)
            (sx, sy, syaw), (gx, gy) = task or self.sample_task(a)
            if math.hypot(gx - sx, gy - sy) < 1.0 or not a.pose_free(sx, sy, syaw, 0.02):
                if task:
                    break
                continue
            self.path = a.plan((sx, sy), (gx, gy))
            if self.path is not None:
                break
        self.robot = S.Robot(a, sx, sy, syaw, rng=self.rng)
        self.goal = (gx, gy)
        self.steps = 0
        self.d_prev = self.dist()
        self.state = self.robot.state(gx, gy)
        return self.state

    def dist(self):
        return math.hypot(self.goal[0] - self.robot.x, self.goal[1] - self.robot.y)

    def step(self, action):
        v, w = P.action_to_cmd(action)
        self.robot.step(v, w)
        self.steps += 1
        d = self.dist()
        s2 = self.robot.state(*self.goal)
        closest = s2[:P.N_SECTORS].min() * P.MAX_RANGE
        r = 8.0 * (self.d_prev - d) - 0.03 - 0.03 * abs(w)
        if closest < 0.5:
            r -= 2.0 * (0.5 - closest)
        # footprint clearance (privileged, training only): keep ~10 cm off things
        clear = self.robot.arena.clearance(self.robot.x, self.robot.y, self.robot.yaw)
        if clear < 0.10:
            r -= 3.0 * (0.10 - max(clear, 0.0)) / 0.10
        self.d_prev = d
        info = {'arrived': False, 'crashed': False, 'timeout': False}
        done = False
        if self.robot.crashed:
            r -= 15.0
            done = info['crashed'] = True
        elif d < self.arrive:
            r += 15.0
            done = info['arrived'] = True
        elif self.steps >= self.max_steps:
            info['timeout'] = True                 # not terminal for bootstrapping
        self.state = s2
        return s2, r, done, info

    # ------------------------------------------------------------- expert
    def expert_action(self, lookahead=0.55):
        """Pure pursuit along the privileged grid path (training data only)."""
        rb = self.robot
        path = self.path
        if not path:
            return P.cmd_to_action(0.0, 0.0)
        d = [math.hypot(px - rb.x, py - rb.y) for px, py in path]
        i = int(np.argmin(d))
        self.path = path = path[i:]
        target = path[-1]
        for px, py in path:
            if math.hypot(px - rb.x, py - rb.y) >= lookahead:
                target = (px, py)
                break
        e = P.wrap(math.atan2(target[1] - rb.y, target[0] - rb.x) - rb.yaw)
        w = float(np.clip(2.2 * e, -P.W_MAX, P.W_MAX))
        v = P.V_MAX * max(0.0, math.cos(e)) ** 3
        v = min(v, 0.8 * self.dist() + 0.15)
        return P.cmd_to_action(v, w)
