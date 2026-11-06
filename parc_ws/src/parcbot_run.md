# Terminal 1
colcon build --symlink-install
source /opt/ros/jazzy/setup.bash && source install/setup.bash
ros2 launch task_solution slam_launch.py

# Terminal 2
colcon build --symlink-install
source /opt/ros/jazzy/setup.bash && source install/setup.bash
ros2 run task_solution tag_mapper --ros-args -p use_sim_time:=true \
        -p output_file:=~/teams/ARCX6/src/task_solution/maps/tags.yaml

# Terminal 3
colcon build --symlink-install
source /opt/ros/jazzy/setup.bash && source install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/botwheel_explorer/cmd_vel -p stamped:=true -p frame_id:=base_link

# Terminal 4
colcon build --symlink-install
source /opt/ros/jazzy/setup.bash && source install/setup.bash
ros2 run nav2_map_server map_saver_cli -f ~/teams/ARCX6/src/task_solution/maps/nov6_map_save

# Solution
## T1
ros2 launch task_solution task_solution.launch.py map:=/home/jachin/FINAL-ARCX6-PARC/parc_ws/src/task_solution/maps/nov5_sd1_map_save.yaml tags_file:=/home/jachin/FINAL-ARCX6-PARC/parc_ws/src/task_solution/maps/tags.yaml

## T2
ros2 launch parc_referee referee.launch.py odom_topic:=/botwheel_explorer/odom and go to Link

## T3
ros2 run task_solution start_run 

or 

ros2 run task_solution voice_start --ros-args -p model_path:=/home/jachin/FINAL-ARCX6-PARC/models/vosk-model-small-en-us-0.15 to use voice cmd