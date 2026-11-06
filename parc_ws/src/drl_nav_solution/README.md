# drl_nav_solution

Map-free PARC 2026 solution with two parts:

* a **view planner** that decides where to look for tags not found yet, replacing
  explore_solution's fixed sweep. This is where most of the time is saved, and
  it works with either driver;
* an optional **deep-reinforcement-learning driver** trained with
  **PEEMEF-DARC** (He et al., *Learning Autonomous Navigation in Unmapped and
  Unknown Environments*, Sensors 2024, 24(18) 5925,
  [code](https://github.com/nfhe/darc_drl_nav)).

**Nav2 drives by default** (`driver:=nav2`). The learned policy (`driver:=drl`) has
only been trained and tested in a 2D copy of the arena. Check it in Gazebo, then on
the real robot at low speed, before relying on it in a run.

```bash
cd ~/parc_ws && colcon build --symlink-install --packages-select drl_nav_solution && source install/setup.bash

ros2 launch parc_robot_bringup phase2_hard.launch.py seed:=7                    # terminal 1
ros2 launch parc_referee referee.launch.py odom_topic:=/botwheel_explorer/odom  # terminal 2
ros2 launch drl_nav_solution drl_solution.launch.py                             # terminal 3 (Nav2 drives)
#   or: ros2 launch drl_nav_solution drl_solution.launch.py driver:=drl           # learned policy drives
ros2 run task_solution start_run                                                # terminal 4, after arming
```

The robot must start at the official start pose: the view planner places the
arena (7 m x 6 m, start 1 m in front of the back wall, centred) relative to it.

## What runs

| Part | From | What it does |
| --- | --- | --- |
| `drl_visitor` | this package, subclass of `explore_solution.ExploreVisitor` | Run logic, referee, tag detection, camera alignment and 3 s hold are unchanged. Exploration is replaced; with `driver:=drl` the driving legs are too. |
| DARC policy | `weights/darc_policy.npz` | With `driver:=drl`: drives to the approach point of a tag and to viewpoints: 24 range sectors + goal distance/angle + last command → (v, w) at 10 Hz. No costmap, no planner. |
| View planner | `view_planner.py` | Picks where to turn around next to find the tags not seen yet (see below). |
| slam_toolbox | `task_solution/slam_launch.py` | Only keeps map→odom free of drift so recorded tag positions stay put. Nothing is planned on its map. |
| Nav2 | as in `explore_solution` (rolling live costmap, no saved map) | `driver:=nav2`: drives every leg. `driver:=drl`: finishes a leg when the policy makes no 0.1 m progress in 4 s (`nav2_fallback:=false` turns that off). |

### The policy (PEEMEF-DARC)

Ported from the paper's code to Python 3 / numpy (the robot does not need PyTorch):

* **DARC**: two actors, two critics, cross-updated; target value is a soft mix of
  the min and max of the two actors' clipped double-Q values; critic
  regularisation `(Q1 − Q2)²`; when acting, the actor whose critic rates its
  action higher wins.
* **PEEM**: the replay buffer starts with expert demonstrations, and each batch
  mixes in "excellent" (highest-reward) transitions.
* **State**: the paper's 28 numbers. The 24 ranges come from `/scan_merged`
  (lidar + both depth cameras) plus 3 s of remembered nearby points, because the
  lidar sees only the 4 cm centre column of a cafe table while the robot (~1.2 m
  tall) hits the 0.76 m top, and the scan merger drops returns closer than 0.3 m.

Changes from the paper, all to fit this robot and a timed run:

| Paper | Here | Why |
| --- | --- | --- |
| Reward caps speed near 0.2 m/s | No cap, time penalty | The run is timed; the robot does 0.5 m/s |
| Huge penalties for turning | Small `|w|` penalty | Tight arena needs turning |
| Human demonstrations (`human_data.mat`) | Grid-path expert in the 2D sim | No human data for this robot |
| Re-sorts the whole buffer every step, ~70 % excellent samples | Top 5 % refreshed every 2000 steps, share decays 50 % → 10 % | Speed; lets the agent outgrow the demos |
| — | Behaviour-cloning warm start of both actors | Makes CPU-only training practical |
| — | Footprint-clearance reward term (training only) | The rectangular footprint is not visible in 24 ranges |
| Gazebo 9 TurtleBot3 corridors | 2D copy of the seeded PARC arenas | Thousands of episodes per hour on a laptop CPU |

### The view planner

Map-free exploration is what takes the time, so the fixed sweep is replaced. The
planner keeps every place a tag could still be, using only the rules: wall tags
≥ 1 m from corners, facing inward; free-standing tags ≥ 1.4 m from walls, any
direction; ≥ 2.2 m between tags; ≥ 1.8 m from the start. A possibility is ruled
out when the camera has had it in view (2.8 m, ±38°, ≤ 55° off the tag face, or
33° for free-standing ones), or when an obstacle was seen inside the
1.5 m × 1.2 m area the generator keeps clear in front of every tag. The next
viewpoint maximises the possibilities a full turn there would check per second
of travel. Points 1.2 m in front of open possibilities are always candidates,
because that area is clear if the tag is real. If nothing is left but a tag is
still missing, it starts over with tighter limits, so a detector weaker than
assumed costs time rather than a tag.

## Launch arguments

| Argument | Default | |
| --- | --- | --- |
| `driver` | `nav2` | `drl` = the learned policy drives |
| `nav2_fallback` | `true` | With `driver:=drl`: Nav2 finishes legs the policy gets stuck on |
| `explorer` | `view` | `sweep` = explore_solution's fixed sweep |
| `drl_cmd_topic` | `cmd_vel_smoothed` | Through the collision monitor (safe, slows near obstacles). `/cmd_vel` = direct |
| `spin_speed` | `0.9` | rad/s while turning to look for tags (explore_solution: 0.4) |
| `max_speed` | `0.4` | Nav2 top speed (explore_solution: 0.35) |
| `policy_file` | packaged weights | Another `.npz` from training |
| `use_sim_time`, `base_frame` | `true`, `base_footprint` | Real robot: `false`, `base_link` |

Node parameters (`--ros-args -p` or a params file): `view_range`,
`view_half_fov_deg`, `view_off_face_deg` (lower them if the detector misses tags
the planner thinks it checked), `arena_bounds`, `drl_stuck_s`, `memory_s`.

## Training and evaluation (no ROS needed)

```bash
cd parc_ws/src/drl_nav_solution
python3 -m drl_nav_solution.training.train --steps 200000 --out weights/darc_policy.npz
python3 -m drl_nav_solution.training.evaluate_run --driver drl --policy weights/darc_policy.npz \
    --explorer view --spin-speed 0.9 --max-speed 0.4 --approach 0.85 --region 0.25 --seeds 1-30
python3 -m pytest -q test
```

`training/sim2d.py` builds each arena with `parc_robot_bringup.world_generator`
(same seed, same obstacle shapes as Gazebo) and models the SITO-E footprint,
velocity and acceleration limits, the lidar (table and chair legs only), the
±45° depth cameras (full shapes) and the 0.3 m range cut-off. Training uses arena
seeds 100–399, validation 1000–1019, and the run evaluation above uses 1–30.

## Results (2D simulation, 20 held-out arenas, seeds 1–20)

Full 4-tag runs, 10-minute limit, simulated with `training/evaluate_run.py`. In
these runs "Nav2" is a stand-in: grid path + pure pursuit + recoveries, planned
on the **true** obstacle layout. That flatters it, because real Nav2 only knows
what it has seen. The camera alignment is timed, not simulated.

| Setup | Runs completed | Tags reported | Mean / median / max time of completed runs |
| --- | --- | --- | --- |
| A: explore_solution today (sweep, Nav2 0.35 m/s, 0.4 rad/s spins) | 8 / 20 | 62 / 80 | 255 / 242 / 405 s |
| **B: view planner + Nav2 (`driver:=nav2`, default)** | **16 / 20** | **73 / 80** | **170 / 148 / 334 s** |
| C: view planner + DARC policy (`driver:=drl`) | 15 / 20 | 71 / 80 | 157 / 139 / 268 s |

* The view planner is the big gain: twice as many completed runs and roughly 40 % less time than the fixed sweep.
* The policy is a little quicker on the runs it completes. But Nav2 took over 98 of its 230 legs (43 %), mostly where an obstacle sits between the robot and the goal and the memoryless policy dithers between going left and going right.
* The remaining failures in B and C are mostly the robot squeezing into a ~0.55 m gap (for example between a wall and a table corner) and getting trapped, or a tag the camera never had a clear enough view of.

Policy on single navigation legs (validation arenas 1000–1019, 60 legs): 75 %
reach the goal, 8 % collide, 17 % time out. The packaged weights are the 100k-step
checkpoint of a 200k-step run that was stopped at about 120k.


## Limits and next steps

* **Trained in 2D, not in Gazebo.** Check it in Gazebo before trusting it: the
  sensor model is approximate (no depth-camera noise beyond a simple model, no
  wheel slip, perfect odometry), and the alignment step is only timed, not
  simulated. Fine-tuning in Gazebo means porting `NavEnv` to
  ros_gz (`/world/parc_random/set_pose` for resets); the trainer and the
  networks stay the same.
* **Trap gaps.** Both drivers sometimes enter gaps barely wider than the robot.
  Raising Nav2's inflation radius (and, for the policy, retraining with a larger
  clearance penalty) would help.
* **Collision monitor.** Through `cmd_vel_smoothed` the monitor slows the policy
  near obstacles, which the 2D sim does not model. If it makes runs slow,
  try `drl_cmd_topic:=/cmd_vel` only after watching it drive safely in Gazebo.
* **Start pose.** The view planner assumes the robot starts at the official
  start pose. Started elsewhere, set `arena_bounds` or use `explorer:=sweep`.
* **Detector range.** `view_range` 2.8 m assumes the AprilTag detector decodes
  the 0.15 m tags out to ~3 m (explore_solution's note). Check this in Gazebo.
