"""ARCX6 no-prior-map solution: wheel odometry + live SLAM + camera-coverage exploration.

    ros2 launch live_solution live_solution.launch.py                                   # sim
    ros2 launch live_solution live_solution.launch.py use_sim_time:=false base_frame:=base_link   # robot
    ros2 run task_solution start_run          # after the judge arms the run

Starts odom_fix (wheel odometry with corrected rotation -> frame odom_fixed),
slam_toolbox (mapping on odom_fixed, tuned for this robot), Nav2 (task_solution's tuning,
planning on the live SLAM map + live obstacles) and live_visitor.

odom_yaw_scale: rotation correction for the wheel odometry, default 1.0 (off). Two
simulator measurements disagreed (-10 % and +24 %), so it stays off until the factor is
measured reliably; set it with odom_yaw_scale:=<factor> once known.

SLAM tuning vs task_solution's mapping config: scans are added every 0.2 m / 0.2 rad
(not 0.5 / 0.5) and the scan-match search window is 4x larger, so in-place scan spins
and wheel slip are corrected instead of breaking the map.
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


def slam_params(odom_frame):
    src = os.path.join(get_package_share_directory('task_solution'), 'config',
                       'mapper_params_online_async.yaml')
    with open(src) as f:
        p = yaml.safe_load(f)
    s = p['slam_toolbox']['ros__parameters']
    s.update({
        'mode': 'mapping',
        'odom_frame': odom_frame,
        'minimum_travel_distance': 0.2,
        'minimum_travel_heading': 0.2,
        'minimum_time_interval': 0.2,
        'map_update_interval': 1.0,
        'correlation_search_space_dimension': 1.0,
        'correlation_search_space_resolution': 0.01,
        'loop_search_maximum_distance': 4.0,
        'do_loop_closing': True,
    })
    out = os.path.join(tempfile.gettempdir(), 'live_solution_slam.yaml')
    with open(out, 'w') as f:
        yaml.safe_dump(p, f, sort_keys=False)
    return out


def nav2_params(max_speed):
    src = os.path.join(get_package_share_directory('task_solution'), 'config', 'nav2_params.yaml')
    with open(src) as f:
        p = yaml.safe_load(f)
    g = p['global_costmap']['global_costmap']['ros__parameters']
    g['track_unknown_space'] = True               # plan on the live SLAM map (static layer)
    v = float(max_speed)
    fp = p['controller_server']['ros__parameters']['FollowPath']
    fp['max_vel_x'] = v
    fp['max_speed_xy'] = v
    p['velocity_smoother']['ros__parameters']['max_velocity'][0] = v
    out = os.path.join(tempfile.gettempdir(), 'live_solution_nav2.yaml')
    with open(out, 'w') as f:
        yaml.safe_dump(p, f, sort_keys=False)
    return out


def launch_setup(context):
    lc = lambda n: LaunchConfiguration(n).perform(context)  # noqa: E731
    use_sim_time = LaunchConfiguration('use_sim_time')
    base_frame = LaunchConfiguration('base_frame')
    ts = os.path.join(get_package_share_directory('task_solution'), 'launch')
    scale = lc('odom_yaw_scale')
    if scale == 'auto':
        scale = '1.0'     # correction off until measured reliably (two sim tests disagreed)
    return [
        Node(package='live_solution', executable='odom_fix', name='odom_fix', output='screen',
             parameters=[{'use_sim_time': use_sim_time, 'yaw_scale': float(scale)}]),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(ts, 'slam_launch.py')),
            launch_arguments={'use_sim_time': use_sim_time, 'base_frame': base_frame,
                              'slam_params_file': slam_params('odom_fixed')}.items()),
        TimerAction(period=5.0, actions=[IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(ts, 'navigation_launch.py')),
            launch_arguments={'use_sim_time': use_sim_time, 'base_frame': base_frame,
                              'params_file': nav2_params(lc('max_speed'))}.items())]),
        TimerAction(period=10.0, actions=[Node(
            package='live_solution', executable='live_visitor', name='tag_visitor', output='screen',
            parameters=[{'use_sim_time': use_sim_time, 'base_frame': base_frame,
                         'image_topic': LaunchConfiguration('image_topic'),
                         'camera_info_topic': LaunchConfiguration('camera_info_topic')}])]),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true', description='false on the real robot'),
        DeclareLaunchArgument('base_frame', default_value='base_footprint',
                              description='base_footprint (sim), base_link (real robot)'),
        DeclareLaunchArgument('max_speed', default_value='0.3', description='Nav2 top speed, m/s'),
        DeclareLaunchArgument('odom_yaw_scale', default_value='auto',
                              description="odometry rotation correction factor ('auto' = 1.0, i.e. off)"),
        DeclareLaunchArgument('image_topic', default_value='/camera1/camera1/color/image_raw',
                              description='colour camera used to read the tags'),
        DeclareLaunchArgument('camera_info_topic', default_value='/camera1/camera1/color/camera_info'),
        OpaqueFunction(function=launch_setup),
    ])
