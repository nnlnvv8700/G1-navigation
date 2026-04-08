#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd $SCRIPT_DIR
source ./install/setup.bash
pkill -f 'ros2 launch vehicle_simulator system_real_robot_with_exploration_planner.launch.py' 2>/dev/null || true
pkill -f 'livox_ros_driver2_node' 2>/dev/null || true
pkill -f 'feature_extraction_node|laser_mapping_node|imu_preintegration_node' 2>/dev/null || true
sleep 1
ros2 launch vehicle_simulator system_real_robot_with_exploration_planner.launch.py "$@" &
sleep 1
ros2 run rviz2 rviz2 -d src/exploration_planner/tare_planner/rviz/tare_planner_ground.rviz
