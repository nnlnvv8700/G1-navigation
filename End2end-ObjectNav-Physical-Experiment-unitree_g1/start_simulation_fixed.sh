#!/bin/bash

# 清理之前的进程
echo "清理旧进程..."
sudo pkill -9 -f 'ros|Model.x86_64' 2>/dev/null
sleep 2

# 清理环境变量冲突
unset GTK_PATH
unset SNAP

# 配置ROS环境
echo "配置ROS环境..."
source /opt/ros/jazzy/setup.bash
source install/setup.sh

# 设置机器人配置
export ROBOT_CONFIG_PATH="mechanum_drive"
echo "机器人配置: $ROBOT_CONFIG_PATH"

# 启动仿真
echo "启动仿真系统..."
./system_simulation.sh
