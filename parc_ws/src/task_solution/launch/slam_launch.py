"""Build a map of the arena with slam_toolbox (mapping mode).

    ros2 launch parc_robot_bringup phase2_hard.launch.py seed:=7
    ros2 launch task_solution slam_launch.py
    ros2 run task_solution tag_mapper --ros-args -p use_sim_time:=true \
        -p output_file:=$HOME/ARCX6FINALREPO/FINAL-ARCX6-PARC/parc_ws/src/task_solution/maps/tags.yaml
    # drive around, then save the occupancy grid for map_server/AMCL:
    ros2 run nav2_map_server map_saver_cli -f <path>/maps/<name>

Do not run this together with task_solution.launch.py: AMCL and slam_toolbox
would both publish map -> odom.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg = get_package_share_directory('task_solution')
    slam_pkg = get_package_share_directory('slam_toolbox')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument(
            'slam_params_file',
            default_value=os.path.join(pkg, 'config', 'mapper_params_online_async.yaml')),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(slam_pkg, 'launch', 'online_async_launch.py')),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'slam_params_file': LaunchConfiguration('slam_params_file'),
            }.items(),
        ),
    ])
