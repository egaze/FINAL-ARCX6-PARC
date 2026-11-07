# explore_solution — ARCX6, PARC 2026 Engineers League

Visits the four AprilTags in the referee's order **without mapping the arena first**.
The robot finds the tags during the run.

## Run

Build once (the workspace must contain `task_solution` and `explore_solution`):

```bash
cd parc_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

Simulation (any seed):

```bash
ros2 launch parc_robot_bringup phase2_hard.launch.py seed:=7          # the arena
ros2 launch explore_solution explore_solution.launch.py               # our solution
ros2 launch parc_referee referee.launch.py odom_topic:=/botwheel_explorer/odom
# arm the run on the dashboard, then start it:
ros2 run task_solution start_run
```

Real robot:

```bash
ros2 launch explore_solution explore_solution.launch.py use_sim_time:=false base_frame:=base_link
ros2 run task_solution start_run
```

## How it works

1. **Waits** for the referee to be RUNNING (no movement before: no false start).
2. **Localization without mapping** (`localization:=arena`, default): only the arena
   outline from the rules is used (7 m x 6 m, robot starts 1 m in front of the back wall,
   centred). AMCL localizes against those four walls. Tags and obstacles are discovered
   live. `localization:=slam` uses no prior knowledge at all (map built during the run).
3. **Search**, cheapest clue first, until the next tag in the order is known:
   1. the tag was decoded at least once, even far away (ID exact): drive towards it;
   2. an unread tag-like square was seen repeatedly on the camera horizon (tags are at
      camera height): go and look;
   3. otherwise the next point of a sweep across the arena, with a scan spin.
   Every tag seen on the way is remembered for later.
4. **Visit** (from `task_solution`): approach region in front of the tag, smooth camera
   alignment to 0.5 m and square-on, JPEG `TagVisit`, 3 s hold, back out.
5. Missed tags get a second pass while time is left; then `Finish`.

Tag checks: AprilTag 36h11 only, exact codes (0 corrected bits), IDs 1/4/7/9, several
decodes within 2 s. Obstacles: lidar and both depth cameras (tabletops) in the local
costmap and the collision monitor.

## Useful arguments

| Argument | Default | |
|---|---|---|
| `use_sim_time` | `true` | `false` on the real robot |
| `base_frame` | `base_footprint` | `base_link` on the real robot |
| `localization` | `arena` | `arena` or `slam` |
| `robot` | `false` | `true`: real robot (`config/nav2_params_robot.yaml`, no sim clock, `base_link`, live SLAM) |
| `max_speed` | *(from file)* | Nav2 top speed override, m/s (files: sim 0.35, robot 0.25; robot max 0.5) |
| `cmd_vel_topic` | `/cmd_vel` | simulation only: where the collision monitor sends Twist |
| `arena_back/front/left/right` | `1.0/5.0/3.5/3.5` | arena walls relative to the start pose |

## Nav2 parameters and velocity commands

`robot:=false` loads `config/nav2_params_sim.yaml`, `robot:=true` loads
`config/nav2_params_robot.yaml`. Both are task_solution's tuning with the explore
adaptations; they differ only in the robot frame (`base_link`), the live-SLAM global
costmap, the top speed and the velocity message type/topic below.

```
controller_server ─┐
behavior_server ───┴─> cmd_vel_nav ─> velocity_smoother ─> cmd_vel_smoothed ─> collision_monitor ─> wheels
explore_visitor (align, scan spins, back-outs; only while Nav2 is silent) ───────┘
```

| | message type (`enable_stamped_cmd_vel`) | collision monitor output |
|---|---|---|
| simulation | `geometry_msgs/Twist` (False on all 4 nodes) | `/cmd_vel` |
| real robot | `geometry_msgs/TwistStamped` (True on all 4 nodes), frame `base_link` | `/botwheel_explorer/cmd_vel` |

Nothing else publishes to the wheels: no relay, no bypass. explore_visitor yields to Nav2
until `cmd_vel_nav` has been silent for 1.1 s (the smoother's 1.0 s `velocity_timeout`).
