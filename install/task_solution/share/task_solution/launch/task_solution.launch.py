"""ARCX6 solution: everything the robot runs during a scored run.

    ros2 launch task_solution task_solution.launch.py
    ros2 launch task_solution task_solution.launch.py map:=/abs/path/arena.yaml tags_file:=/abs/path/tags.yaml

Starts, in order:
  1. localization  (map_server + AMCL on the saved map)
  2. navigation    (Nav2, after 5 s)
  3. tag_visitor   (after 10 s): waits for the referee to be RUNNING, then visits
                   the tags in /parc/tag_order and reports each one.

The robot does not move until the referee is RUNNING. Start the run with
    ros2 run task_solution start_run

Build the map and tags.yaml for the arena beforehand with slam_launch.py
(see that file). The defaults are maps/arena.yaml and maps/tags.yaml in this
package; rebuild the package after replacing them.
"""

import os
import shutil

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('task_solution')
    launch_dir = os.path.join(pkg, 'launch')

    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')

    args = [
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Use the Gazebo clock (false on the real robot)'),
        DeclareLaunchArgument('map', default_value=os.path.join(pkg, 'maps', 'arena.yaml'),
                              description='Occupancy map yaml for AMCL / Nav2'),
        DeclareLaunchArgument('tags_file', default_value=os.path.join(pkg, 'maps', 'tags.yaml'),
                              description='Tag positions in the map frame (from tag_mapper)'),
        DeclareLaunchArgument('params_file',
                              default_value=os.path.join(pkg, 'config', 'nav2_params.yaml'),
                              description='Nav2 parameters'),
    ]

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(launch_dir, 'localization_launch.py')),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'use_sim_time': use_sim_time,
            'params_file': params_file,
        }.items(),
    )

    navigation = TimerAction(period=5.0, actions=[
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, 'navigation_launch.py')),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'params_file': params_file,
            }.items(),
        ),
    ])

    tag_visitor = TimerAction(period=10.0, actions=[
        Node(
            package='task_solution',
            executable='tag_visitor',
            name='tag_visitor',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'tags_file': LaunchConfiguration('tags_file'),
            }],
        ),
    ])

    checks = []
    # Hybrid-graphics laptops with an NVIDIA GPU render on the integrated GPU (or the CPU)
    # unless PRIME offload is selected. AMD / Intel GPUs use Mesa and need nothing here
    # (on a hybrid AMD laptop, DRI_PRIME=1 picks the discrete GPU).
    if shutil.which('nvidia-smi') and os.environ.get('__NV_PRIME_RENDER_OFFLOAD') != '1':
        checks.append(LogInfo(msg=(
            'WARNING: this machine has an NVIDIA GPU but this terminal does not select it '
            '(__NV_PRIME_RENDER_OFFLOAD is not 1). If Gazebo was started from a terminal like '
            'this, it renders on the integrated GPU or CPU and runs several times slower. '
            'Open a new terminal (or "source ~/.bashrc") and restart the simulation.')))

    return LaunchDescription(args + checks + [localization, navigation, tag_visitor])
