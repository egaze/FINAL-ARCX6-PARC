"""Minimal fallback: apriltag_ros (or OpenCV) + depth, potential-field driving. No Nav2/SLAM/AMCL.

    ros2 launch tag_tracker tag_tracker.launch.py                 # sim
    ros2 launch tag_tracker tag_tracker.launch.py robot:=true     # real robot
    ros2 run task_solution start_run          # after the judge arms the run

robot:=true = no sim clock, base_link, TwistStamped straight to /botwheel_explorer/cmd_vel
(frame base_link), 0.2 m/s. Processes: tracker, depth_obstacles, apriltag container,
slam_toolbox (slam:=true).

Pose: with a camera IMU publishing (pose_source:=auto) the tracker uses gyro heading + wheel
speed (in the sim the wheel odometry yaw is ~13 % off per turn; the gyro 0.5 %). Without IMU
data it falls back to TF: 'map' from slam_toolbox (slam:=true) or raw 'odom' (slam:=false).

Live tuning while it runs (no restart):
    ros2 param set /tag_tracker max_linear_x 0.2
    ros2 param set /tag_tracker max_angular_z 0.6
    ros2 param set /tag_tracker repulsive_gain 0.08
    ros2 param set /tag_tracker detector opencv        # if apriltag_ros misbehaves
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context):
    lc = lambda n: LaunchConfiguration(n).perform(context)  # noqa: E731
    robot = lc('robot').lower() == 'true'
    sim = False if robot else lc('use_sim_time').lower() == 'true'
    base = 'base_link' if robot else lc('base_frame')
    cmd = '/botwheel_explorer/cmd_vel' if robot else lc('cmd_vel_topic')
    stamped = True if robot else lc('stamped').lower() == 'true'
    vmax = float(lc('max_linear_x')) if lc('max_linear_x') else (0.2 if robot else 0.25)
    # tag camera = forward-looking top camera: camera1 in the sim, camera2 on the real robot
    cam = lc('tag_camera').strip()
    if cam == 'auto':
        cam = 'camera2' if robot else 'camera1'
    ns = lc('camera_namespace').strip().strip('/') or f'{cam}/{cam}/color'
    depth_topic = lc('depth_topic').strip() or f'/{cam}/{cam}/depth/image_rect_raw'
    imu_topic = lc('imu_topic').strip() or f'/{cam}/{cam}/imu'
    slam = lc('slam').lower() == 'true'
    cams = [c.strip() for c in lc('depth_cameras').split(',') if c.strip()]
    actions = [LogInfo(msg=f'tag_tracker: robot={robot} sim_time={sim} base={base} cmd={cmd} '
                           f'camera=/{ns} stamped={stamped} v={vmax} detector={lc("detector")} '
                           f'cameras={cams} slam={slam}')]
    if slam:
        actions.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(
                get_package_share_directory('task_solution'), 'launch', 'slam_launch.py')),
            launch_arguments={'use_sim_time': str(sim).lower(), 'base_frame': base}.items()))
    if lc('detector') == 'apriltag':
        actions.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(
                get_package_share_directory('parcbot_docking'), 'launch', 'apriltag_dock_pose_publisher.py')),
            launch_arguments={'camera_namespace': ns, 'use_sim_time': str(sim).lower()}.items()))
    actions += [
        # depth cameras -> 3D obstacle points (tabletops the lidar passes under)
        Node(package='task_solution', executable='depth_obstacles', name='depth_obstacles',
             output='screen', parameters=[{'use_sim_time': sim, 'base_frame': base, 'cameras': cams}]),
        Node(package='tag_tracker', executable='minimal_tag_tracker', name='tag_tracker',
             output='screen',
             parameters=[{'use_sim_time': sim, 'base_frame': base,
                          'max_linear_x': vmax,
                          'max_angular_z': float(lc('max_angular_z')),
                          'detector': lc('detector'),
                          'image_topic': f'/{ns}/image_raw',
                          'camera_info_topic': f'/{ns}/camera_info',
                          'detections_topic': f'/{ns}/detections',
                          'depth_topic': depth_topic,
                          'cloud_topics': [f'/depth_obstacles/{c}' for c in cams],
                          'cmd_vel_topic': cmd,
                          'odom_frame': 'map' if slam else 'odom',
                          'pose_source': lc('pose_source'),
                          'imu_topic': imu_topic,
                          'stamped': stamped}]),
    ]
    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('robot', default_value='false',
                              description='true on the real robot (sets the options below)'),
        DeclareLaunchArgument('slam', default_value='true',
                              description='live slam_toolbox map for a drift-free heading'),
        DeclareLaunchArgument('pose_source', default_value='auto',
                              description='auto: gyro heading + wheel speed if imu_topic publishes, '
                                          'else TF (map with slam:=true); or imu / tf'),
        DeclareLaunchArgument('imu_topic', default_value='', description='empty: /<cam>/<cam>/imu'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('base_frame', default_value='base_footprint',
                              description='base_footprint (sim), base_link (real robot)'),
        DeclareLaunchArgument('max_linear_x', default_value='',
                              description='m/s; empty = 0.25 sim / 0.2 robot'),
        DeclareLaunchArgument('max_angular_z', default_value='0.8'),
        DeclareLaunchArgument('detector', default_value='apriltag', description='apriltag or opencv'),
        DeclareLaunchArgument('tag_camera', default_value='auto',
                              description='auto: camera1 in the sim, camera2 with robot:=true'),
        DeclareLaunchArgument('camera_namespace', default_value='', description='empty: <cam>/<cam>/color'),
        DeclareLaunchArgument('depth_topic', default_value='', description='empty: /<cam>/<cam>/depth/image_rect_raw'),
        DeclareLaunchArgument('depth_cameras', default_value='camera1,camera2'),
        DeclareLaunchArgument('cmd_vel_topic', default_value='/cmd_vel'),
        DeclareLaunchArgument('stamped', default_value='false',
                              description='publish TwistStamped (robot preset sets it)'),
        OpaqueFunction(function=launch_setup),
    ])
