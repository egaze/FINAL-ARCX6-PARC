"""Map-free ARCX6 solution: explore during the run, find the tags, visit them in order.

    ros2 launch explore_solution explore_solution.launch.py               # simulation (nav2_params_sim.yaml)
    ros2 launch explore_solution explore_solution.launch.py robot:=true   # real robot (nav2_params_robot.yaml)

Then arm the run on the referee dashboard and start it:
    ros2 run task_solution start_run

No mapping session is needed. Localization (`localization:=`):
  * arena (default): the PARC arena walls are fixed by the rules (7 m x 6 m; the robot
    starts 1 m in front of the back wall, centred, facing into the arena; only the tags
    and obstacles change with the seed). A map of just those four walls is generated
    here and AMCL localizes against it, starting at (0, 0). Absolute, no drift.
    Measured with live SLAM instead: 1.9 m / 27 deg off after a few minutes (wheel slip),
    so remembered tag positions and sweep points landed in the wrong place.
  * slam: slam_toolbox builds the map during the run (use when the arena size is unknown).
    Set the arena_* arguments if the real arena differs from the simulated one.

Also starts Nav2 (task_solution's launch files, parameters from this package's
config/nav2_params_{sim,robot}.yaml) and explore_visitor (after 10 s).

Velocity commands (one chain, the collision monitor is always the last step):
  controller_server / behavior_server -> cmd_vel_nav -> velocity_smoother -> cmd_vel_smoothed
  explore_visitor's own moves (alignment, spins, back-outs) -> cmd_vel_smoothed, only while
      Nav2 is silent (it yields to Nav2)
  cmd_vel_smoothed -> collision_monitor -> /cmd_vel (sim, Twist)
                                        -> /botwheel_explorer/cmd_vel (robot, TwistStamped)
"""

import os
import tempfile

import numpy as np
import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription, LogInfo,
                            OpaqueFunction, TimerAction)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

RES = 0.05
# robot:=true start: the robot starts in a corner of the arena, so it first drives out of it
ROBOT_OPENING = 'forward 3.0, left 90, forward 4.3'


def arena_map(back, front, left, right):
    """Occupancy map of the four arena walls in the start frame (x forward, y left)."""
    margin = 0.5
    x0, y0 = -back - margin, -right - margin
    w = int(round((front + back + 2 * margin) / RES))
    h = int(round((left + right + 2 * margin) / RES))
    img = np.full((h, w), 205, np.uint8)                  # unknown outside
    def cx(x): return int(round((x - x0) / RES))          # noqa: E704
    def cy(y): return int(round((y - y0) / RES))          # noqa: E704
    img[cy(-right):cy(left) + 1, cx(-back):cx(front) + 1] = 254   # free inside
    for c in (cx(-back), cx(front)):                      # walls, 2 cells thick
        img[cy(-right):cy(left) + 1, c - 1:c + 1] = 0
    for r in (cy(-right), cy(left)):
        img[r - 1:r + 1, cx(-back):cx(front) + 1] = 0
    d = os.path.join(tempfile.gettempdir(), 'explore_solution_arena')
    os.makedirs(d, exist_ok=True)
    pgm = os.path.join(d, 'arena_walls.pgm')
    with open(pgm, 'wb') as f:                            # row 0 of a PGM is the top (max y)
        f.write(f'P5\n{w} {h}\n255\n'.encode())
        f.write(np.flipud(img).tobytes())
    yml = os.path.join(d, 'arena_walls.yaml')
    with open(yml, 'w') as f:
        yaml.safe_dump({'image': pgm, 'mode': 'trinary', 'resolution': RES,
                        'origin': [float(x0), float(y0), 0.0], 'negate': 0,
                        'occupied_thresh': 0.65, 'free_thresh': 0.196}, f)
    return yml


def explore_nav2_params(robot, max_speed='', live_map=False, depth_cameras=('camera1', 'camera2'),
                        cmd_vel_out=None):
    """Load config/nav2_params_robot.yaml (robot) or config/nav2_params_sim.yaml (simulation).

    Everything static lives in those two files, including the velocity chain (Twist in the
    sim, TwistStamped on the robot). Only choices made on the command line are applied here:
    a top-speed override, a live global costmap for localization:=slam in the sim (the robot
    file already has it), the depth cameras the robot really has, and the sim's output topic.
    """
    name = 'nav2_params_robot.yaml' if robot else 'nav2_params_sim.yaml'
    src = os.path.join(get_package_share_directory('explore_solution'), 'config', name)
    with open(src) as f:
        params = yaml.safe_load(f)
    g = params['global_costmap']['global_costmap']['ros__parameters']
    if live_map and 'static_layer' in g['plugins']:
        g['plugins'] = ['obstacle_layer', 'inflation_layer']
        g.pop('static_layer', None)
        g['rolling_window'] = True
        g['width'] = 14
        g['height'] = 14
        g['track_unknown_space'] = False
    # Only use depth cameras the robot really has: the collision monitor STOPS the robot
    # when any of its sources goes silent (a missing camera2 would block all motion).
    keep = set(depth_cameras)
    for cm, layer in (('local_costmap', 'voxel_layer'), ('global_costmap', 'obstacle_layer')):
        lay = params[cm][cm]['ros__parameters'].get(layer)
        if lay is None:
            continue
        srcs = lay['observation_sources'].split()
        drop = [x for x in srcs if x.startswith('camera') and x.split('_')[0] not in keep]
        lay['observation_sources'] = ' '.join(x for x in srcs if x not in drop)
        for x in drop:
            lay.pop(x, None)
    cmon = params['collision_monitor']['ros__parameters']
    if cmd_vel_out:
        cmon['cmd_vel_out_topic'] = cmd_vel_out
    cmon_drop = [x for x in cmon['observation_sources'] if x.startswith('camera') and x.split('_')[0] not in keep]
    cmon['observation_sources'] = [x for x in cmon['observation_sources'] if x not in cmon_drop]
    for x in cmon_drop:
        cmon.pop(x, None)
    if max_speed:
        v = float(max_speed)
        fp = params['controller_server']['ros__parameters']['FollowPath']
        fp['max_vel_x'] = v
        fp['max_speed_xy'] = v
        params['velocity_smoother']['ros__parameters']['max_velocity'][0] = v
    out = os.path.join(tempfile.gettempdir(),
                       f'explore_solution_{"robot" if robot else "sim"}_nav2_params.yaml')
    with open(out, 'w') as f:
        yaml.safe_dump(params, f, sort_keys=False)
    return out, src


def launch_setup(context):
    lc = lambda n: LaunchConfiguration(n).perform(context)  # noqa: E731
    use_sim_time = LaunchConfiguration('use_sim_time')
    base_frame = LaunchConfiguration('base_frame')
    mode = lc('localization')
    max_speed = lc('max_speed')
    robot = lc('robot').lower() == 'true'
    if robot:
        # Real-robot preset: no sim clock, robot frame base_link, live SLAM (no prior map or
        # arena size). Speed (0.25 m/s), TwistStamped commands and the wheel topic
        # (/botwheel_explorer/cmd_vel, written by the collision monitor) come from
        # config/nav2_params_robot.yaml.
        use_sim_time, base_frame, mode = 'false', 'base_link', 'slam'
        cmd_vel_out = None
    else:
        cmd_vel_out = lc('cmd_vel_topic')
    # Node parameters need a real bool; launch arguments (includes) need text.
    sim_param = (use_sim_time.lower() == 'true') if isinstance(use_sim_time, str) else use_sim_time
    ts_launch = os.path.join(get_package_share_directory('task_solution'), 'launch')
    cams = tuple(c.strip() for c in lc('depth_cameras').split(',') if c.strip())
    # Tag camera = the forward-looking top camera: camera1 in the sim, camera2 on the real
    # robot (there camera1 is the one tilted down at the floor).
    cam = lc('tag_camera').strip()
    if cam == 'auto':
        cam = 'camera2' if robot else 'camera1'
    cam_ns = lc('camera_namespace').strip().strip('/') or f'{cam}/{cam}/color'
    depth_topic = lc('depth_topic').strip() or f'/{cam}/{cam}/depth/image_rect_raw'
    opening = lc('opening').strip()
    if opening == 'auto':                     # robot: out of the start corner first
        opening = ROBOT_OPENING if robot else ''
    elif opening == 'robot':                  # the robot's opening, also in the sim
        opening = ROBOT_OPENING
    elif opening == 'none':
        opening = ''
    params_file, params_src = explore_nav2_params(robot, max_speed, live_map=(mode == 'slam'),
                                                  depth_cameras=cams, cmd_vel_out=cmd_vel_out)
    composed = lc('use_composition').lower() == 'true'
    comp_args = {'use_composition': 'True' if composed else 'False', 'container_name': 'nav2_container'}
    actions = [LogInfo(msg=f'explore_solution: tags from /{cam_ns}/image_raw (depth {depth_topic})'),
               LogInfo(msg=f'explore_solution: Nav2 parameters from {params_src} '
                           f'({"TwistStamped -> /botwheel_explorer/cmd_vel" if robot else "Twist -> " + cmd_vel_out})')]
    if composed:
        # All Nav2 servers (+ AMCL/map server in arena mode) in ONE process = one DDS
        # participant. CycloneDDS allows ~10 participants per host by default, and the robot's
        # own programs already use several ("Failed to find a free participant index").
        actions += [
            Node(package='rclcpp_components', executable='component_container_isolated',
                 name='nav2_container', output='screen',
                 parameters=[params_file, {'autostart': True, 'use_sim_time': sim_param}],
                 remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')]),
            # depth cameras -> 3D obstacle points (only started by task_solution's
            # navigation launch in non-composed mode)
            Node(package='task_solution', executable='depth_obstacles', name='depth_obstacles',
                 output='screen', parameters=[{'use_sim_time': sim_param, 'base_frame': base_frame,
                                               'cameras': list(cams)}]),
        ]
    if mode == 'slam':
        actions.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(ts_launch, 'slam_launch.py')),
            launch_arguments={'use_sim_time': use_sim_time, 'base_frame': base_frame}.items()))
    else:
        walls = arena_map(float(lc('arena_back')), float(lc('arena_front')),
                          float(lc('arena_left')), float(lc('arena_right')))
        actions += [
            LogInfo(msg=f'explore_solution: localizing with AMCL on the arena walls ({walls}).'),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(os.path.join(ts_launch, 'localization_launch.py')),
                launch_arguments={'use_sim_time': use_sim_time, 'base_frame': base_frame,
                                  'map': walls, 'params_file': params_file, **comp_args}.items()),
        ]
    if lc('detector') == 'apriltag':
        # apriltag_ros on the tag camera (parcbot_docking's rectify + detector container);
        # it publishes /<cam_ns>/detections and TF frames tag_1/4/7/9
        actions.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(
                get_package_share_directory('parcbot_docking'), 'launch', 'apriltag_dock_pose_publisher.py')),
            launch_arguments={'camera_namespace': cam_ns,
                              'use_sim_time': use_sim_time}.items()))
    actions += [
        TimerAction(period=5.0, actions=[IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(ts_launch, 'navigation_launch.py')),
            launch_arguments={'use_sim_time': use_sim_time, 'params_file': params_file,
                              'base_frame': base_frame, **comp_args}.items())]),
        TimerAction(period=10.0, actions=[Node(
            package='explore_solution', executable='explore_visitor',
            name='tag_visitor',              # same name: same log lines / parameters as before
            output='screen',
            parameters=[{'use_sim_time': sim_param, 'base_frame': base_frame,
                         'arena_bounds': ([-float(lc('arena_back')), float(lc('arena_front')),
                                           -float(lc('arena_right')), float(lc('arena_left'))]
                                          if mode != 'slam' else [0.0]),
                         'detector': LaunchConfiguration('detector'),
                         # own moves -> cmd_vel_smoothed (collision monitor input), same
                         # message type as the Nav2 chain in this mode
                         'stamped_cmd_vel': robot,
                         'opening': opening,
                         # approach region 0.6 m from the tag (was 0.75): with a table in front of
                         # a tag (0.93 m to the tabletop in the test world) 0.75 m left the robot's
                         # centre inside its footprint margin of the tabletop; the photo pose is 0.5 m
                         'approach_distance': 0.6,
                         'image_topic': f'/{cam_ns}/image_raw',
                         'camera_info_topic': f'/{cam_ns}/camera_info',
                         'detections_topic': f'/{cam_ns}/detections',
                         'depth_topic': depth_topic}])]),
    ]
    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='false on the real robot'),
        DeclareLaunchArgument('base_frame', default_value='base_footprint',
                              description='robot body frame: base_footprint (sim), base_link (real robot)'),
        DeclareLaunchArgument('localization', default_value='arena',
                              description='arena (AMCL on the known arena walls) or slam (map built live)'),
        DeclareLaunchArgument('detector', default_value='apriltag',
                              description='apriltag (apriltag_ros, reads far tags) or opencv'),
        DeclareLaunchArgument('tag_camera', default_value='auto',
                              description='camera that reads the tags (the forward-looking top one): '
                                          'auto = camera1 in the sim, camera2 with robot:=true'),
        DeclareLaunchArgument('camera_namespace', default_value='',
                              description='override the colour namespace (empty: <cam>/<cam>/color); '
                                          'image_raw, camera_info and detections live under it'),
        DeclareLaunchArgument('depth_topic', default_value='',
                              description='override the tag-range depth image (empty: '
                                          '/<cam>/<cam>/depth/image_rect_raw)'),
        DeclareLaunchArgument('robot', default_value='false',
                              description='true on the real robot: config/nav2_params_robot.yaml '
                                          '(TwistStamped -> /botwheel_explorer/cmd_vel, 0.25 m/s), no '
                                          'sim clock, base_link, live SLAM; false: nav2_params_sim.yaml'),
        DeclareLaunchArgument('opening', default_value='auto',
                              description='moves at the start of the run before the search, e.g. '
                                          '"forward 1.3, left 90, forward 1.0" (m, deg; also back, '
                                          f'right). auto: robot "{ROBOT_OPENING}", sim none; robot: "{ROBOT_OPENING}" '
                                          'in the sim too; none: off'),
        DeclareLaunchArgument('cmd_vel_topic', default_value='/cmd_vel',
                              description="simulation only: the collision monitor's output topic "
                                          '(where the simulated wheels listen, Twist)'),
        DeclareLaunchArgument('use_composition', default_value='true',
                              description='run all Nav2 servers in one process (fewer DDS participants)'),
        DeclareLaunchArgument('depth_cameras', default_value='camera1,camera2',
                              description='depth cameras the robot really has, e.g. camera1 (a missing '
                                          'one would make the collision monitor block all motion)'),
        DeclareLaunchArgument('max_speed', default_value='',
                              description='Nav2 top speed override in m/s (empty: from the params file, '
                                          'sim 0.35 / robot 0.25; robot max 0.5)'),
        # Arena walls relative to the start pose (PARC phase 2 arena from the README)
        DeclareLaunchArgument('arena_back', default_value='1.0', description='m behind the start'),
        DeclareLaunchArgument('arena_front', default_value='5.0', description='m in front of the start'),
        DeclareLaunchArgument('arena_left', default_value='3.5', description='m to the left of the start'),
        DeclareLaunchArgument('arena_right', default_value='3.5', description='m to the right of the start'),
        OpaqueFunction(function=launch_setup),
    ])
