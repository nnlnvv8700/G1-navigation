#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cleanup() {
  pkill -f 'ros2 launch vehicle_simulator system_real_robot.launch.py' 2>/dev/null || true
  pkill -f 'livox_ros_driver2_node' 2>/dev/null || true
  pkill -f 'feature_extraction_node|laser_mapping_node|imu_preintegration_node' 2>/dev/null || true
  pkill -f '/install/local_planner/lib/local_planner/localPlanner' 2>/dev/null || true
  pkill -f '/install/local_planner/lib/local_planner/pathFollower' 2>/dev/null || true
}

cd $SCRIPT_DIR
source ./install/setup.bash
trap cleanup INT TERM EXIT
cleanup
sleep 1
ros2 launch vehicle_simulator system_real_robot.launch.py "$@" &
sleep 1
ros2 run rviz2 rviz2 -d src/base_autonomy/vehicle_simulator/rviz/vehicle_simulator.rviz
