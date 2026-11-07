"""Map-free ARCX6 solution: explore during the run, find the tags, visit them in order.

    ros2 launch explore_solution explore_solution.launch.py                      # simulation
    ros2 launch explore_solution explore_solution.launch.py use_sim_time:=false base_frame:=base_link   # real robot

Then arm the run on the referee dashboard and start it:
    ros2 run task_solution start_run

Starts:
  * slam_toolbox in mapping mode (task_solution's slam_launch.py): it builds the map
    during the run and keeps correcting wheel-odometry drift with the lidar. No saved
    map is needed. (An odometry-only version was tested first: wheel slip against
    obstacles drifted 3.7 m in 5 minutes, so tags were recorded in the wrong place.)
  * Nav2 from task_solution (same tuning), but its global costmap is a live 14 m x 14 m
    obstacle map built from the lidar instead of a saved map;
  * explore_visitor (after 8 s).
"""

import os
import tempfile

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction,
                            TimerAction)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def explore_nav2_params(max_speed):
    """task_solution's Nav2 parameters with the saved-map layer replaced by a live map,
    and a lower top speed (no map: obstacles are only known once the sensors see them)."""
    src = os.path.join(get_package_share_directory('task_solution'), 'config', 'nav2_params.yaml')
    with open(src) as f:
        params = yaml.safe_load(f)
    g = params['global_costmap']['global_costmap']['ros__parameters']
    g['plugins'] = ['obstacle_layer', 'inflation_layer']
    g.pop('static_layer', None)
    g['rolling_window'] = True              # follows the robot; no map needed
    g['width'] = 14
    g['height'] = 14
    g['track_unknown_space'] = False        # unseen space counts as free until the lidar sees it
    v = float(max_speed)
    fp = params['controller_server']['ros__parameters']['FollowPath']
    fp['max_vel_x'] = v
    fp['max_speed_xy'] = v
    vs = params['velocity_smoother']['ros__parameters']
    vs['max_velocity'][0] = v
    out = os.path.join(tempfile.gettempdir(), 'explore_solution_nav2_params.yaml')
    with open(out, 'w') as f:
        yaml.safe_dump(params, f, sort_keys=False)
    return out


def launch_setup(context):
    use_sim_time = LaunchConfiguration('use_sim_time')
    base_frame = LaunchConfiguration('base_frame')
    ts_launch = os.path.join(get_package_share_directory('task_solution'), 'launch')
    nav_launch = os.path.join(ts_launch, 'navigation_launch.py')
    return [
        # Live SLAM: publishes map -> odom and corrects odometry drift as the robot drives.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(ts_launch, 'slam_launch.py')),
            launch_arguments={'use_sim_time': use_sim_time, 'base_frame': base_frame}.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav_launch),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'params_file': explore_nav2_params(LaunchConfiguration('max_speed').perform(context)),
                'base_frame': base_frame,
            }.items(),
        ),
        TimerAction(period=8.0, actions=[
            Node(
                package='explore_solution', executable='explore_visitor',
                name='tag_visitor',          # same name: same log lines / parameters as before
                output='screen',
                parameters=[{'use_sim_time': use_sim_time, 'base_frame': base_frame}],
            ),
        ]),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='false on the real robot'),
        DeclareLaunchArgument('base_frame', default_value='base_footprint',
                              description='robot body frame: base_footprint (sim), base_link (real robot)'),
        DeclareLaunchArgument('max_speed', default_value='0.35',
                              description='Nav2 top speed in m/s (robot max 0.5). Lower = safer without a map'),
        OpaqueFunction(function=launch_setup),
    ])
