"""Simulate complete PARC runs (4 tags, map-free) in the 2D arena and time them.

    python3 -m drl_nav_solution.training.evaluate_run --policy weights/darc_policy.npz --seeds 1-30

Replays explore_solution's run logic step by step at 10 Hz:
  start spin -> for each tag in the order: sweep + spins until it has been seen
  (camera model below) -> drive to its approach point -> camera alignment ->
  report -> 3 s hold -> back out.

Driver modes:
  drl     policy drives every leg; if it makes no 0.1 m progress in 4 s (or the
          collision monitor would have stopped it) the leg is finished by the
          'nav2' driver below, as in drl_visitor with nav2_fallback:=true.
  nav2    stand-in for Nav2: pure pursuit along a grid path at <= max_speed.
          The path is planned on the TRUE obstacle map, so this is optimistic
          for Nav2 (the real one only knows what its sensors have seen).

Camera model: the tag is decoded if it is within 3.0 m of the camera, inside
+-40 degrees of the image centre, seen less than 60 degrees off its face normal
and not hidden behind an obstacle; 3 frames in a row make a sighting, 3
sightings make a tag known (explore_visitor's min_consecutive / min_samples).

Camera alignment and the 0.5 m stop are not simulated in detail: they cost
2 s + distance / 0.25 m/s + turn / 0.8 rad/s, then the robot is placed at the
visit pose. The 3 s hold, 0.3 s settle and 0.35 m back-out are simulated.
"""

import argparse
import json
import math

import numpy as np

from drl_nav_solution import policy as P
from drl_nav_solution.training import sim2d as S
from drl_nav_solution.training.env import approach_point
from drl_nav_solution.view_planner import ViewPlanner


def to_map(x, y, yaw=0.0):
    """World -> run map frame (origin at the start pose (0, -7), facing +y)."""
    return y + 7.0, -x, yaw - math.pi / 2


def to_world(mx, my):
    return -my, mx - 7.0

DT = S.DT
DEFAULT_SWEEP = [1.0, 0.0, 1.0, -2.2, 2.5, -2.2, 4.0, -2.2, 4.0, 0.0,
                 2.5, 0.0, 2.5, 2.2, 4.0, 2.2, 1.0, 2.2]


class RunSim:
    def __init__(self, seed, driver, policy=None, max_speed=0.35, spin_speed=0.4,
                 approach=0.75, region=0.20, order_seed=0, time_limit=600.0, explorer='sweep'):
        self.arena = S.Arena(seed)
        self.explorer = explorer
        self.planner = ViewPlanner(spin_speed=spin_speed, v_travel=max_speed) if explorer == 'view' else None
        self.driver = driver
        self.policy = policy
        self.max_speed = max_speed
        self.spin_speed = spin_speed
        self.approach = approach
        self.region = region
        self.limit = time_limit
        sx, sy, syaw = S.wg.START
        self.robot = S.Robot(self.arena, sx, sy, syaw, rng=np.random.default_rng(seed))
        ids = sorted(self.arena.tags)
        np.random.default_rng(order_seed).shuffle(ids)
        self.order = ids
        self.streak = {i: 0 for i in ids}
        self.samples = {i: 0 for i in ids}
        self.known = set()
        self.reported = []
        self.events = {'fallback_legs': 0, 'policy_legs': 0, 'monitor_stops': 0}
        sweep = DEFAULT_SWEEP
        # sweep points are (forward, left) from the start pose, which faces +y
        self.sweep = [(sx - fy, sy + fx) for fx, fy in zip(sweep[0::2], sweep[1::2])]
        self.next_wp = 0
        self.planner_found = set()
        self.restarts = 0

    @property
    def t(self):
        return self.robot.t

    def out_of_time(self):
        return self.t >= self.limit

    # ---------------------------------------------------------------- camera
    def camera_update(self):
        r = self.robot
        for tid, tag in self.arena.tags.items():
            dx, dy = tag.x - r.x, tag.y - r.y
            d = math.hypot(dx, dy)
            seen = False
            if d <= 3.0:
                bearing = P.wrap(math.atan2(dy, dx) - r.yaw)
                off_face = abs(P.wrap(math.atan2(-dy, -dx) - tag.facing))
                if abs(bearing) <= math.radians(40) and off_face <= math.radians(60):
                    fx, fy = tag.x + 0.05 * math.cos(tag.facing), tag.y + 0.05 * math.sin(tag.facing)
                    seen = self.arena.line_of_sight(r.x, r.y, fx, fy)
            self.streak[tid] = self.streak[tid] + 1 if seen else 0
            if self.streak[tid] >= 3:
                self.samples[tid] += 1
                if self.samples[tid] >= 3:
                    self.known.add(tid)
            self.live_range = getattr(self, 'live_range', {})
            self.live_range[tid] = d if self.streak[tid] >= 3 else None
            if self.planner is not None and tid in self.known and tid not in self.planner_found:
                self.planner_found.add(tid)
                self.planner.tag_found(*to_map(tag.x, tag.y)[:2])
        if self.planner is not None:
            mx, my, myaw = to_map(r.x, r.y, r.yaw)
            cam = self.arena.camera
            self.planner.observe(mx, my, myaw,
                                 lambda a: cam.raycast(r.x, r.y, np.asarray(a) + math.pi / 2))
            self.n_cam = getattr(self, 'n_cam', 0) + 1
            if self.n_cam % 3 == 0:
                c, sn = math.cos(myaw), math.sin(myaw)
                self.planner.add_obstacles(mx + c * r.scan_x - sn * r.scan_y,
                                           my + sn * r.scan_x + c * r.scan_y)

    def step(self, v, w):
        """One 0.1 s step. A step that would hit something is refused (the robot's
        collision monitor would stop it): returns False."""
        r = self.robot
        saved = (r.x, r.y, r.yaw, r.v, r.w, r.t)
        before = self.arena.clearance(r.x, r.y, r.yaw)
        r.step(v, w)
        # Collision monitor: refuse moves that end within 2 cm of something, unless
        # they get further away from it.
        after = self.arena.clearance(r.x, r.y, r.yaw)
        r.crashed = after < 0.02 and after < before
        if r.crashed:
            r.crashed = False
            r.x, r.y, r.yaw, _, _, _ = saved
            r.v = r.w = 0.0
            self.events['monitor_stops'] += 1
            self.camera_update()
            return False
        self.camera_update()
        return True

    # --------------------------------------------------------------- drivers
    def goal_reachable(self, gx, gy):
        g, free = self.arena.free_grid(0.28)
        return bool(free[g.cell(gx, gy)])

    def follow_path(self, gx, gy, stop_fn, timeout):
        if not self.goal_reachable(gx, gy):           # Nav2 rejects goals inside obstacles
            return 'failed'
        path = self.arena.plan((self.robot.x, self.robot.y), (gx, gy), clearance=0.42,
                               fallbacks=(0.38, 0.34))
        if path is None:
            # Usually the robot is too close to something for any path to start:
            # Nav2's recoveries (back up, turn, drive on) get it clear, then replan.
            self.recover()
            path = self.arena.plan((self.robot.x, self.robot.y), (gx, gy), clearance=0.42,
                                   fallbacks=(0.38, 0.34))
        if path is None:
            return 'failed'
        end = self.t + timeout
        stalled = 0
        best, best_at = None, self.t
        while self.t < end and not self.out_of_time():
            res = stop_fn()
            if res:
                return res
            r = self.robot
            dg = math.hypot(gx - r.x, gy - r.y)
            if best is None or dg < best - 0.10:
                best, best_at = dg, self.t
            elif self.t - best_at > 5.0:                # explore_visitor / tag_visitor stuck_time_s
                for _ in range(10):
                    self.step(-0.3, 0.0)
                return 'stuck'
            d = [math.hypot(px - r.x, py - r.y) for px, py in path]
            path = path[int(np.argmin(d)):]
            target = path[-1]
            for px, py in path:
                if math.hypot(px - r.x, py - r.y) >= 0.55:
                    target = (px, py)
                    break
            e = P.wrap(math.atan2(target[1] - r.y, target[0] - r.x) - r.yaw)
            w = float(np.clip(2.2 * e, -1, 1))
            # DWB-like: turn on the spot first when the path is well off the heading
            v = 0.0 if abs(e) > 0.9 else self.max_speed * math.cos(e) ** 3
            v = min(v, 0.8 * math.hypot(gx - r.x, gy - r.y) + 0.15)
            if not self.step(v, w):
                stalled += 1
                if stalled > 20:                       # Nav2 recovery
                    self.recover()
                    path = self.arena.plan((self.robot.x, self.robot.y), (gx, gy), clearance=0.42,
                                           fallbacks=(0.38, 0.34)) or path
                    stalled = 0
            else:
                stalled = 0
        return 'failed'

    def recover(self, want=0.15, max_steps=60):
        """Nav2-style recovery: small moves (back up, turn, creep) chosen greedily
        to gain footprint clearance until there is `want` metres of room."""
        r = self.robot
        moves = [(-0.15, 0.0), (0.15, 0.0), (0.0, 0.6), (0.0, -0.6),
                 (-0.1, 0.5), (-0.1, -0.5), (0.1, 0.5), (0.1, -0.5)]
        for _ in range(max_steps):
            here = self.arena.clearance(r.x, r.y, r.yaw)
            if here >= want:
                break
            best = None
            for v, w in moves:                            # look ahead one 0.3 s move
                yaw = r.yaw + w * 0.3
                x = r.x + v * 0.3 * math.cos(yaw)
                y = r.y + v * 0.3 * math.sin(yaw)
                c = self.arena.clearance(x, y, yaw)
                if best is None or c > best[0]:
                    best = (c, v, w)
            if best[0] <= here + 1e-4:
                break
            r.v = r.w = 0.0
            for _ in range(3):
                self.step(best[1], best[2])
        self.stop()

    def drive_policy(self, gx, gy, stop_fn, timeout):
        end = self.t + timeout
        best, best_at = None, self.t
        self.events['policy_legs'] += 1
        while self.t < end and not self.out_of_time():
            res = stop_fn()
            if res:
                return res
            r = self.robot
            d = math.hypot(gx - r.x, gy - r.y)
            if best is None or d < best - 0.10:
                best, best_at = d, self.t
            elif self.t - best_at > 4.0:
                return 'stuck'
            v, w = P.action_to_cmd(self.policy.act(r.state(gx, gy)))
            if not self.step(v, w):
                return 'stuck'
        return 'failed'

    def drive(self, gx, gy, stop_fn, timeout):
        if self.driver == 'nav2':
            return self.follow_path(gx, gy, stop_fn, timeout)
        res = self.drive_policy(gx, gy, stop_fn, timeout)
        if res == 'stuck':
            self.events['fallback_legs'] += 1
            # back off a little first, like the real fallback's recovery
            for _ in range(5):
                self.step(-0.15, 0.0)
            res = self.follow_path(gx, gy, stop_fn, timeout)
        return res

    # ------------------------------------------------------------ behaviours
    def spin_scan(self, target):
        """explore_visitor.spin_scan: one turn, time limit 2*pi/speed + 6 s."""
        turned = 0.0
        end = self.t + 2 * math.pi / self.spin_speed + 6.0
        while turned < 2 * math.pi and self.t < end and not self.out_of_time():
            if target in self.known:
                break
            last = self.robot.yaw
            if not self.step(0.0, self.spin_speed):
                if not self.step(-0.15, 0.0):
                    self.step(0.15, 0.0)
            turned += abs(P.wrap(self.robot.yaw - last))
        self.stop()

    def stop(self):
        while (abs(self.robot.v) > 1e-3 or abs(self.robot.w) > 1e-3) and not self.out_of_time():
            self.step(0.0, 0.0)

    def explore_until_known(self, tag):
        if self.planner is not None:
            return self.explore_view(tag)
        while tag not in self.known and self.next_wp < len(self.sweep) and not self.out_of_time():
            x, y = self.sweep[self.next_wp]
            self.next_wp += 1

            def stop_fn():
                if tag in self.known:
                    return 'found'
                if math.hypot(x - self.robot.x, y - self.robot.y) <= 0.35:
                    return 'arrived'
                return None
            self.drive(x, y, stop_fn, 40.0)
            if tag not in self.known:
                self.spin_scan(tag)
        return tag in self.known

    def explore_view(self, tag):
        while tag not in self.known and not self.out_of_time():
            mx, my, _ = to_map(self.robot.x, self.robot.y)
            vp = self.planner.next_viewpoint(mx, my)
            if vp is None and self.restarts < 2:          # as drl_visitor
                self.restarts += 1
                self.planner.restart_strict()
                vp = self.planner.next_viewpoint(mx, my)
            if vp is None:
                return False
            x, y = to_world(*vp)

            def stop_fn():
                if tag in self.known:
                    return 'found'
                if math.hypot(x - self.robot.x, y - self.robot.y) <= 0.35:
                    return 'arrived'
                return None
            self.drive(x, y, stop_fn, 40.0)
            self.planner.used(*vp)
            if tag not in self.known:
                self.spin_scan(tag)
                mx, my, _ = to_map(self.robot.x, self.robot.y)
                self.planner.used(mx, my)
        return tag in self.known

    def visit(self, tag):
        t = self.arena.tags[tag]
        ax, ay = approach_point(t, self.approach)

        def stop_fn():
            if math.hypot(ax - self.robot.x, ay - self.robot.y) <= self.region:
                return 'in_region'
            rng = self.live_range.get(tag) if hasattr(self, 'live_range') else None
            if rng is not None and rng <= 1.2:
                return 'tag_in_view'
            return None
        res = self.drive(ax, ay, stop_fn, 120.0)
        if res == 'failed':
            return False
        self.stop()
        vx, vy, vyaw = t.visit_pose()
        r = self.robot
        dist = math.hypot(vx - r.x, vy - r.y)
        turn = abs(P.wrap(math.atan2(vy - r.y, vx - r.x) - r.yaw)) + abs(P.wrap(vyaw - r.yaw))
        r.t += 2.0 + dist / 0.25 + turn / 0.8
        r.x, r.y, r.yaw, r.v, r.w = vx, vy, vyaw, 0.0, 0.0
        r.memory.clear()
        r.sense()
        r.t += 0.3 + 0.2 + 3.1                         # settle, capture, hold
        if self.out_of_time():
            return False
        self.reported.append(tag)
        start = (r.x, r.y)
        while math.hypot(r.x - start[0], r.y - start[1]) < 0.35 and not self.out_of_time():
            if not self.step(-0.3, 0.0):
                break
        self.stop()
        return True

    def run(self):
        self.camera_update()
        self.spin_scan(self.order[0])
        for tag in self.order:
            if self.out_of_time():
                break
            if tag not in self.known and not self.explore_until_known(tag):
                continue
            self.visit(tag)
        for tag in [t for t in self.order if t not in self.reported]:   # second pass
            if self.out_of_time():
                break
            if tag not in self.known:
                self.next_wp = 0
                if not self.explore_until_known(tag):
                    continue
            self.visit(tag)
        done = len(self.reported) == 4
        return {'seed': self.arena.seed, 'tags': len(self.reported),
                'time_s': round(min(self.t, self.limit), 1) if done else None, **self.events}


def parse_seeds(text):
    out = []
    for part in text.split(','):
        if '-' in part:
            a, b = part.split('-')
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--policy', default=None)
    ap.add_argument('--seeds', default='1-20')
    ap.add_argument('--driver', choices=['drl', 'nav2'], default='drl')
    ap.add_argument('--max-speed', type=float, default=0.35)
    ap.add_argument('--spin-speed', type=float, default=0.4)
    ap.add_argument('--approach', type=float, default=0.75)
    ap.add_argument('--region', type=float, default=0.20)
    ap.add_argument('--explorer', choices=['sweep', 'view'], default='sweep')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    pol = P.Policy(a.policy) if a.policy else None
    results = []
    for seed in parse_seeds(a.seeds):
        sim = RunSim(seed, a.driver, pol, a.max_speed, a.spin_speed, a.approach, a.region,
                     order_seed=seed, explorer=a.explorer)
        res = sim.run()
        results.append(res)
        print(json.dumps(res), flush=True)
    times = [r['time_s'] for r in results if r['time_s'] is not None]
    summary = {'driver': a.driver, 'explorer': a.explorer, 'max_speed': a.max_speed,
               'spin_speed': a.spin_speed, 'runs': len(results), 'completed': len(times),
               'tags_reported': sum(r['tags'] for r in results),
               'mean_time_s': round(float(np.mean(times)), 1) if times else None,
               'median_time_s': round(float(np.median(times)), 1) if times else None,
               'max_time_s': max(times) if times else None,
               'fallback_legs': sum(r['fallback_legs'] for r in results),
               'policy_legs': sum(r['policy_legs'] for r in results),
               'monitor_stops': sum(r['monitor_stops'] for r in results)}
    print(json.dumps(summary))
    if a.out:
        with open(a.out, 'w') as f:
            json.dump({'summary': summary, 'runs': results}, f, indent=1)


if __name__ == '__main__':
    main()
