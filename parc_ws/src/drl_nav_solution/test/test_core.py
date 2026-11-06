"""Tests that need no ROS: observation, policy file, view planner, simulator.

    cd parc_ws/src/drl_nav_solution && python3 -m pytest -q test
"""

import math
import os

import numpy as np
import pytest

from drl_nav_solution import policy as P
from drl_nav_solution.view_planner import ViewPlanner

HERE = os.path.dirname(os.path.abspath(__file__))
WEIGHTS = os.path.join(HERE, '..', 'weights', 'darc_policy.npz')


def test_sectors_front_and_left():
    s = P.sectors_from_points(np.array([1.0, 0.0]), np.array([0.0, 2.0]))
    assert s.shape == (P.N_SECTORS,)
    assert s[0] == pytest.approx(1.0 / P.MAX_RANGE)            # straight ahead
    assert s[P.N_SECTORS // 4] == pytest.approx(2.0 / P.MAX_RANGE)   # 90 deg left
    assert s[P.N_SECTORS // 2] == 1.0                          # behind: nothing


def test_state_layout_and_action_mapping():
    st = P.build_state(np.ones(P.N_SECTORS), 3.5, math.pi / 2, 0.25, -0.5)
    assert st.shape == (P.STATE_DIM,) and st[-4:].tolist() == [0.5, 0.5, 0.5, -0.5]
    for v, w in ((0.0, 0.0), (0.5, 1.0), (0.2, -0.3)):
        assert P.action_to_cmd(P.cmd_to_action(v, w)) == pytest.approx((v, w))


def test_memory_expires_and_transforms():
    m = P.ObstacleMemory(horizon=1.0, keep_range=5.0)
    m.add(0.0, [1.0], [0.0])
    x, y = m.robot_frame(0.0, 0.0, math.pi / 2)        # robot facing +y: point is to its right
    assert x[0] == pytest.approx(0.0, abs=1e-9) and y[0] == pytest.approx(-1.0)
    m.add(2.0, [], [])
    assert len(m.robot_frame(0, 0, 0)[0]) == 0


@pytest.mark.skipif(not os.path.exists(WEIGHTS), reason='no trained weights')
def test_policy_outputs_valid_command():
    pol = P.Policy(WEIGHTS)
    a = pol.act(P.build_state(np.ones(P.N_SECTORS), 3.0, 0.0, 0.0, 0.0))
    v, w = P.action_to_cmd(a)
    assert 0.0 <= v <= P.V_MAX and -P.W_MAX <= w <= P.W_MAX
    assert v > 0.2, 'open space with the goal ahead should drive forward'


def test_planner_only_clears_what_the_camera_saw():
    pl = ViewPlanner()
    before = pl.open.copy()
    pl.observe(2.0, 0.0, 0.0, lambda a: np.full(np.shape(a), np.inf))   # looking +x, nothing in the way
    cleared = before & ~pl.open
    assert cleared.any()
    dx, dy = pl.hx[cleared] - 2.0, pl.hy[cleared]
    assert np.all(np.hypot(dx, dy) <= pl.cam_range + 1e-9)
    assert np.all(np.abs(np.arctan2(dy, dx)) <= pl.cam_half_fov + 1e-9)


def test_planner_blocked_view_only_clears_by_keep_out_rule():
    pl = ViewPlanner()
    before = pl.open.copy()
    pl.observe(2.0, 0.0, 0.0, lambda a: np.full(np.shape(a), 0.2))      # obstacle 0.2 m ahead
    cleared = np.flatnonzero(before & ~pl.open)
    # Only hypotheses whose kept-clear area (1.4 m in front of the tag) contains
    # the obstacle may be ruled out: they must face the robot and be close.
    for i in cleared:
        assert math.hypot(pl.hx[i] - 2.0, pl.hy[i]) <= 0.2 + 1.5
        assert abs(math.atan2(math.sin(pl.hf[i] - math.pi), math.cos(pl.hf[i] - math.pi))) < 1.6
    far = np.hypot(pl.hx - 2.0, pl.hy) > 1.8
    assert np.array_equal(before[far], pl.open[far])


def test_planner_restart_reopens():
    pl = ViewPlanner()
    pl.observe(2.0, 0.0, 0.0, lambda a: np.full(np.shape(a), np.inf))
    pl.tag_found(4.97, 0.0)
    r = pl.cam_range
    pl.restart_strict()
    assert pl.cam_range < r
    assert not pl.open[np.hypot(pl.hx - 4.97, pl.hy) < 2.2].any()      # found tag stays explained
    assert pl.open[np.hypot(pl.hx - 4.97, pl.hy) >= 2.2].sum() > 0


def test_sim_raycast_and_collision():
    sim2d = pytest.importorskip('drl_nav_solution.training.sim2d')
    shapes = sim2d.ShapeSet([sim2d.wg.Box(0.0, -5.0, 0.5, 0.5, 0.0)])
    d = shapes.raycast(0.0, -7.0, np.array([math.pi / 2]))[0]
    assert d == pytest.approx(1.5, abs=1e-6)
    arena = sim2d.Arena(1)
    assert arena.pose_free(*sim2d.wg.START)
