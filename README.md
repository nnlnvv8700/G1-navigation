# unitree_project

这是当前工作区的根入口文档，主要说明这个仓库怎么操作、平时该从哪里进入、以及仿真/实机/G1 接入的常用命令。

## 项目组成

根目录下目前主要有两个实际开发子项目：

- `End2end-ObjectNav-Physical-Experiment/`
  - 主导航工作空间
  - 包含 `Livox Mid-360` 驱动、`arise_slam_mid360`、基础自主导航、路线规划、探索规划、Unity 仿真和实机启动脚本
- `g1_ros_package/`
  - `Unitree G1` 相关 ROS2 包
  - 当前你实际在用的是 `controller/g1_controller`
  - 作用是把 ROS2 的 `/cmd_vel` 转发给 `g1_loco_client`

其他目录：

- `.git_backup/`、`.git_backup_20260408_190250/`
  - 旧 Git 历史备份，平时不用动
- `rosbag2_2026_04_02-21_09_12/`
  - 本地 bag 数据目录，不参与代码编译

## 推荐理解方式

你可以把整个仓库理解成两层：

1. `End2end-ObjectNav-Physical-Experiment`
作用：
- 负责感知、SLAM、规划、RViz、仿真与实机主链路

2. `g1_ros_package/controller/g1_controller`
作用：
- 负责把导航输出的 `/cmd_vel` 速度指令接到 `Unitree G1`

也就是说：

- 如果你在改 `MID360`、`SLAM`、导航、launch、RViz，就主要在 `End2end-ObjectNav-Physical-Experiment/`
- 如果你在改 G1 底层速度桥接，就主要在 `g1_ros_package/controller/g1_controller/`

## 最常用进入方式

进入主导航工程：

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment
```

进入 G1 控制桥接工程：

```bash
cd /home/mhw/unitree_project/g1_ros_package
```

## 环境准备

建议系统环境：

- Ubuntu 24.04
- ROS2 Jazzy

先加载 ROS2：

```bash
source /opt/ros/jazzy/setup.bash
```

如果你已经编译过主导航工作空间：

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment
source install/setup.bash
```

如果你已经编译过 G1 工作空间：

```bash
cd /home/mhw/unitree_project/g1_ros_package
source install/setup.bash
```

## 日常操作流程

### 1. 改主导航代码

适用场景：

- 改 `featureExtraction.cpp`
- 改 `arize_slam.launch.py`
- 改 `local_planner`
- 改 `livox_ros_driver2`
- 改 `vehicle_simulator` 启动脚本

常用流程：

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
```

如果只想编一个包，例如 `arise_slam_mid360`：

```bash
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release \
  --packages-select arise_slam_mid360 arise_slam_mid360_msgs
```

如果只编驱动：

```bash
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release \
  --packages-select livox_ros_driver2
```

### 2. 改 G1 控制桥接

适用场景：

- 改 `cmd_vel_to_g1.cpp`
- 改 `cmd_vel_to_g1.launch.py`
- 调整 `g1_loco_client` 路径
- 调整 G1 网卡接口

常用流程：

```bash
cd /home/mhw/unitree_project/g1_ros_package
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select g1_controller
source install/setup.bash
```

启动桥接节点：

```bash
ros2 launch g1_controller cmd_vel_to_g1.launch.py
```

带参数启动：

```bash
ros2 launch g1_controller cmd_vel_to_g1.launch.py \
  network_interface:=enp108s0 \
  g1_loco_client_path:=/home/mhw/robot_g1/unitree_sdk2/build/bin/g1_loco_client \
  unitree_sdk_lib_path:=/home/mhw/robot_g1/unitree_sdk2/thirdparty/lib/x86_64 \
  command_timeout:=0.1
```

## 运行主项目

### 仿真启动

进入主导航目录：

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

启动基础仿真：

```bash
./system_simulation.sh
```

启动带路线规划的仿真：

```bash
./system_simulation_with_route_planner.sh
```

启动带探索规划的仿真：

```bash
./system_simulation_with_exploration_planner.sh
```

说明：

- 仿真依赖 Unity 场景文件
- Unity 模型路径在 `src/base_autonomy/vehicle_simulator/mesh/unity/environment/`

### 实机启动

进入主导航目录：

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

启动基础实机链路：

```bash
./system_real_robot.sh
```

启动带路线规划：

```bash
./system_real_robot_with_route_planner.sh
```

启动带探索规划：

```bash
./system_real_robot_with_exploration_planner.sh
```

当前实机主链路会拉起：

- `livox_ros_driver2`
- `arise_slam_mid360`
- `local_planner`
- `terrain_analysis`
- `sensor_scan_generation`
- RViz

## 如果要接 Unitree G1

这个点非常关键：

- `End2end-ObjectNav-Physical-Experiment` 的主启动脚本目前不会自动拉起 `g1_controller`
- 所以如果你希望导航输出真正驱动 G1，需要额外开一个终端启动 `g1_controller`

推荐操作顺序：

1. 先启动主导航链路

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment
source /opt/ros/jazzy/setup.bash
source install/setup.bash
./system_real_robot.sh
```

2. 再启动 G1 桥接

```bash
cd /home/mhw/unitree_project/g1_ros_package
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch g1_controller cmd_vel_to_g1.launch.py
```

只要导航链路里有 `/cmd_vel` 输出，桥接节点就会把速度转发给 G1。

## 最常查的文件

主导航 README：

- [README.md](/home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment/README.md)

G1 桥接 README：

- [README.md](/home/mhw/unitree_project/g1_ros_package/controller/g1_controller/README.md)

Mid-360 配置：

- [MID360_config.json](/home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment/src/utilities/livox_ros_driver2/config/MID360_config.json)

SLAM 启动文件：

- [arize_slam.launch.py](/home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment/src/slam/arise_slam_mid360/launch/arize_slam.launch.py)

G1 速度桥接代码：

- [cmd_vel_to_g1.cpp](/home/mhw/unitree_project/g1_ros_package/controller/g1_controller/src/cmd_vel_to_g1.cpp)

## Git 常用操作

查看状态：

```bash
cd /home/mhw/unitree_project
git status
```

提交当前修改：

```bash
git add -A
git commit -m "your message"
git push origin master
```

当前仓库已经指向你自己的 GitHub：

```text
origin -> https://github.com/nnlnvv8700/G1-navigation.git
```

## 常见问题

### 1. 编译后找不到命令

通常是没 `source install/setup.bash`。

### 2. Mid-360 没数据

优先检查：

- 网卡 IP
- 雷达 IP
- `MID360_config.json`

### 3. G1 不响应

优先检查：

- `g1_controller` 是否已启动
- `g1_loco_client` 路径是否正确
- `network_interface` 是否填对
- `/cmd_vel` 是否真的有消息

### 4. RViz 打开了但车不动

这通常不是 RViz 的问题，而是以下链路某一段没通：

- 传感器数据
- 定位/SLAM
- 规划输出
- `/cmd_vel`
- G1 桥接或串口底盘控制

## 推荐使用方式

如果你现在主要在做导航和 SLAM，优先从这里开始：

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment
```

如果你现在主要在调 G1 速度控制，优先从这里开始：

```bash
cd /home/mhw/unitree_project/g1_ros_package
```
