"""Observation, action and inference code shared by the trainer and the ROS node.

The state follows PEEMEF-DARC (He et al., Sensors 2024, 24(18) 5925): 24 range
sectors scaled by 3.5 m, then distance and angle to the goal, then the last
linear and angular command - 28 numbers. Differences from the paper:

  * the 24 values are the closest return in each 15 degree sector of the merged
    scan (lidar + both depth cameras) plus the last 3 s of nearby scan points
    (ObstacleMemory): the lidar only sees the thin centre column of a cafe table
    while the robot (~1.2 m tall) hits the 0.76 m table top, which only the
    forward depth cameras see; and returns closer than 0.3 m are dropped by the
    scan merger, so something right beside the robot would otherwise vanish;
  * distance and the commands are normalised to [0, 1] / [-1, 1].

Inference is plain numpy so the robot does not need PyTorch.
"""

import math

import numpy as np

N_SECTORS = 24
MAX_RANGE = 3.5          # m, as in the paper (TurtleBot3 LDS-01 range)
GOAL_NORM = 7.0          # m, arena diagonal is ~9.2 m; clipped at 1
STATE_DIM = N_SECTORS + 4
ACTION_DIM = 2

V_MAX = 0.5              # m/s, robot limit (gz_control.xacro / velocity_smoother)
W_MAX = 1.0              # rad/s
SECTOR_WIDTH = 2 * math.pi / N_SECTORS
MEMORY_S = 3.0           # s of remembered scan points
MEMORY_RANGE = 1.5       # m: only nearby points are remembered


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


def sectors_from_points(px, py):
    """Robot-frame obstacle points (x forward, y left) -> 24 normalised ranges.
    Sector 0 is centred straight ahead, sectors go anticlockwise."""
    out = np.full(N_SECTORS, MAX_RANGE)
    if len(px):
        r = np.hypot(px, py)
        idx = np.round(np.arctan2(py, px) / SECTOR_WIDTH).astype(int) % N_SECTORS
        np.minimum.at(out, idx, r)
    return np.clip(out / MAX_RANGE, 0.0, 1.0)


def build_state(sectors, goal_dist, goal_angle, last_v, last_w):
    s = np.empty(STATE_DIM)
    s[:N_SECTORS] = sectors
    s[N_SECTORS] = min(goal_dist / GOAL_NORM, 1.0)
    s[N_SECTORS + 1] = goal_angle / math.pi
    s[N_SECTORS + 2] = last_v / V_MAX
    s[N_SECTORS + 3] = last_w / W_MAX
    return s


def action_to_cmd(a):
    """Network action in [-1, 1]^2 -> (v, w). Forward-only like the paper."""
    a = np.clip(a, -1.0, 1.0)
    return V_MAX * (a[0] + 1.0) / 2.0, W_MAX * a[1]


def cmd_to_action(v, w):
    return np.array([np.clip(2.0 * v / V_MAX - 1.0, -1, 1), np.clip(w / W_MAX, -1, 1)])


class ObstacleMemory:
    """Short-lived obstacle points in a fixed (odom) frame. Not a map: points older
    than `horizon` seconds are dropped. Lets the policy keep 'seeing' a table top
    that left the depth cameras' 90 degree view while the robot turns past it."""

    def __init__(self, horizon=MEMORY_S, keep_range=MEMORY_RANGE + 0.5, max_points=8000):
        self.horizon = horizon
        self.keep_range = keep_range
        self.max_points = max_points
        self.chunks = []           # (t, xs, ys)

    def add(self, t, xs, ys):
        if len(xs):
            self.chunks.append((t, np.asarray(xs, float), np.asarray(ys, float)))
        while self.chunks and t - self.chunks[0][0] > self.horizon:
            self.chunks.pop(0)
        while sum(len(c[1]) for c in self.chunks) > self.max_points and len(self.chunks) > 1:
            self.chunks.pop(0)

    def clear(self):
        self.chunks = []

    def robot_frame(self, x, y, yaw):
        if not self.chunks:
            return np.zeros(0), np.zeros(0)
        xs = np.concatenate([c[1] for c in self.chunks]) - x
        ys = np.concatenate([c[2] for c in self.chunks]) - y
        c, s = math.cos(yaw), math.sin(yaw)
        lx, ly = c * xs + s * ys, -s * xs + c * ys
        keep = np.hypot(lx, ly) <= self.keep_range
        return lx[keep], ly[keep]


# ---------------------------------------------------------------- inference
def _mlp(layers, x, out_tanh):
    for i, (W, b) in enumerate(layers):
        x = x @ W + b
        if i < len(layers) - 1:
            x = np.maximum(x, 0.0)
    return np.tanh(x) if out_tanh else x


class Policy:
    """Trained PEEMEF-DARC policy. Like the paper's select_action, both actors
    propose an action and the one its critic values higher is used."""

    def __init__(self, path):
        data = np.load(path)
        self.nets = {}
        for name in ('actor1', 'actor2', 'critic1', 'critic2'):
            n = int(data[f'{name}_n'])
            self.nets[name] = [(data[f'{name}_W{i}'], data[f'{name}_b{i}']) for i in range(n)]

    def act(self, state):
        s = np.asarray(state, float)[None, :]
        a1 = _mlp(self.nets['actor1'], s, True)
        a2 = _mlp(self.nets['actor2'], s, True)
        q1 = _mlp(self.nets['critic1'], np.hstack([s, a1]), False)[0, 0]
        q2 = _mlp(self.nets['critic2'], np.hstack([s, a2]), False)[0, 0]
        return (a1 if q1 >= q2 else a2)[0]
