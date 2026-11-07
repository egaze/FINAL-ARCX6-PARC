"""Map-free ARCX6 solution: view-planner exploration, Nav2 or PEEMEF-DARC driving.

    ros2 launch drl_nav_solution drl_solution.launch.py                       # simulation, Nav2 drives
    ros2 launch drl_nav_solution drl_solution.launch.py driver:=drl           # learned policy drives
    ros2 launch drl_nav_solution drl_solution.launch.py use_sim_time:=false base_frame:=base_link   # real robot
    ros2 launch drl_nav_solution drl_solution.launch.py driver:=drl nav2_fallback:=false  # policy only

Then arm the run on the referee dashboard and start it:
    ros2 run task_solution start_run

Starts:
  * slam_toolbox in mapping mode, only to keep map->odom free of drift
    (no saved map; nothing is planned on it);
  * Nav2 as in explore_solution: drives every leg (driver:=nav2), or only
    takes over when the policy gets stuck (driver:=drl, nav2_fallback:=true);
  * drl_visitor (after 8 s): view-planner exploration + policy driving.
"""

import os
import tempfile

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def fallback_nav2_params(max_speed):
    """task_solution's Nav2 parameters with a rolling live obstacle map instead of a saved map."""
    src = os.path.join(get_package_share_directory('task_solution'), 'config', 'nav2_params.yaml')
    with open(src) as f:
        params = yaml.safe_load(f)
    g = params['global_costmap']['global_costmap']['ros__parameters']
    g['plugins'] = ['obstacle_layer', 'inflation_layer']
    g.pop('static_layer', None)
    g['rolling_window'] = True
    g['width'] = 14
    g['height'] = 14
    g['track_unknown_space'] = False
    v = float(max_speed)
    fp = params['controller_server']['ros__parameters']['FollowPath']
    fp['max_vel_x'] = v
    fp['max_speed_xy'] = v
    params['velocity_smoother']['ros__parameters']['max_velocity'][0] = v
    out = os.path.join(tempfile.gettempdir(), 'drl_solution_nav2_params.yaml')
    with open(out, 'w') as f:
        yaml.safe_dump(params, f, sort_keys=False)
    return out


def launch_setup(context):
    use_sim_time = LaunchConfiguration('use_sim_time')
    base_frame = LaunchConfiguration('base_frame')
    ts_launch = os.path.join(get_package_share_directory('task_solution'), 'launch')
    as_bool = lambda name: LaunchConfiguration(name).perform(context).lower() in ('1', 'true', 'yes')  # noqa: E731
    params = {
        'use_sim_time': use_sim_time,
        'base_frame': base_frame,
        'driver': LaunchConfiguration('driver').perform(context),
        'nav2_fallback': as_bool('nav2_fallback'),
        'drl_cmd_topic': LaunchConfiguration('drl_cmd_topic'),
        'explorer': LaunchConfiguration('explorer'),
        # Faster exploration than explore_solution's defaults (0.4 rad/s spins took
        # ~16 s each); the camera still decodes ~10 frames while a tag is in view.
        'spin_speed': float(LaunchConfiguration('spin_speed').perform(context)),
        # The policy was trained to reach a point 0.85 m in front of a tag within 0.25 m.
        'approach_distance': 0.85,
        'region_radius': 0.25,
    }
    policy_file = LaunchConfiguration('policy_file').perform(context)
    if policy_file:
        params['policy_file'] = policy_file
    return [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(ts_launch, 'slam_launch.py')),
            launch_arguments={'use_sim_time': use_sim_time, 'base_frame': base_frame}.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(ts_launch, 'navigation_launch.py')),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'params_file': fallback_nav2_params(LaunchConfiguration('max_speed').perform(context)),
                'base_frame': base_frame,
            }.items(),
        ),
        TimerAction(period=8.0, actions=[
            Node(package='drl_nav_solution', executable='drl_visitor', name='tag_visitor',
                 output='screen', parameters=[params]),
        ]),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('base_frame', default_value='base_footprint',
                              description='base_footprint (sim), base_link (real robot)'),
        DeclareLaunchArgument('driver', default_value='nav2',
                              description='nav2 (default, safest on the real robot) or drl (learned policy)'),
        DeclareLaunchArgument('nav2_fallback', default_value='true',
                              description='Let Nav2 finish a leg when the policy is stuck'),
        DeclareLaunchArgument('drl_cmd_topic', default_value='cmd_vel_smoothed',
                              description='cmd_vel_smoothed = through the collision monitor; /cmd_vel = direct'),
        DeclareLaunchArgument('explorer', default_value='sweep',
                              description='sweep = broad deterministic coverage, view = view planner'),
        DeclareLaunchArgument('spin_speed', default_value='0.9', description='rad/s while scanning for tags'),
        DeclareLaunchArgument('max_speed', default_value='0.4', description='Nav2 fallback top speed, m/s'),
        DeclareLaunchArgument('policy_file', default_value='',
                              description='Policy .npz (default: the trained one in this package)'),
        OpaqueFunction(function=launch_setup),
    ])
