# unitree_project

这是当前工作区的根入口文档，主要说明这个仓库怎么操作、平时该从哪里进入、以及仿真/实机/G1 接入的常用命令。

## 项目组成

根目录下目前主要有三个实际开发子项目：

- `End2end-ObjectNav-Physical-Experiment/`
  - 主导航工作空间
  - 包含 `Livox Mid-360` 驱动、`arise_slam_mid360`、基础自主导航、路线规划、探索规划、Unity 仿真和实机启动脚本

- `End2end-ObjectNav-Physical-Experiment-unitree_g1/`
  - 面向 `Unitree G1` 收口过的一套导航工作空间
  - 默认控制链是 `unitree_webrtc_ros`
  - 当前更适合作为 G1 实机默认入口

- `g1_ros_package/`
  - `Unitree G1` 相关 ROS2 包
  - 当前你实际在用的是 `controller/g1_controller`
  - 作用是把 ROS2 的 `/cmd_vel` 转发给 `g1_loco_client`
  - 更适合作为 G1 控制的 `Plan B`

## 推荐理解方式

你可以把整个仓库理解成三层：

1. `End2end-ObjectNav-Physical-Experiment`
作用：
- 负责感知、SLAM、规划、RViz、仿真与实机主链路

2. `End2end-ObjectNav-Physical-Experiment-unitree_g1`
作用：
- 负责 G1 默认实机链路
- 在原导航工程上接入了 `unitree_webrtc_ros`
- 默认思路是 `/cmd_vel -> unitree_webrtc_ros -> G1`

3. `g1_ros_package/controller/g1_controller`
作用：
- 负责把导航输出的 `/cmd_vel` 速度指令接到 `Unitree G1`
- 这是备用控制链，不是当前首选

也就是说：

- 如果你在改 `MID360`、`SLAM`、导航、launch、RViz，就主要在 `End2end-ObjectNav-Physical-Experiment/`
- 如果你在改 G1 默认实机启动、WebRTC 控制、G1 参数配置，就主要在 `End2end-ObjectNav-Physical-Experiment-unitree_g1/`
- 如果你在改 G1 底层速度桥接，就主要在 `g1_ros_package/controller/g1_controller/`

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

如果你已经编译过 G1 默认工作空间：

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment-unitree_g1
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

这里分两种方案。

### 方案 A：默认推荐方案

默认推荐直接使用：

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment-unitree_g1
```

这套工程已经按 G1 收口过，默认控制链是：

```text
/cmd_vel -> unitree_webrtc_ros/unitree_control -> Unitree WebRTC -> G1
```

这条链路下：

- 不需要再额外启动 `g1_controller`
- 默认更适合当作 G1 实机主入口
- `Plan B` 只在 WebRTC 控制链不可用时再启用

首次上 G1 前，建议先完成这些事：

1. 安装基础环境

```bash
sudo apt update
sudo apt install ros-jazzy-desktop-full ros-jazzy-pcl-ros libpcl-dev git cmake \
  libgoogle-glog-dev libgflags-dev libatlas-base-dev libeigen3-dev libsuitesparse-dev
```

2. 编译 `Livox-SDK2` 和 `livox_ros_driver2`
3. 编译 `Sophus`、`Ceres Solver`、`GTSAM`
4. 编译 `arise_slam_mid360` 与 `arise_slam_mid360_msgs`
5. 安装 `unitree_webrtc_connect`，并准备好 `~/unitree_venv`
6. 编译整个 `End2end-ObjectNav-Physical-Experiment-unitree_g1`
7. 启动前确认 `ROBOT_CONFIG_PATH=unitree/unitree_g1`

推荐启动顺序：

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment-unitree_g1
source /opt/ros/jazzy/setup.bash
source ~/unitree_venv/bin/activate
source install/setup.bash
export ROBOT_CONFIG_PATH="unitree/unitree_g1"
./system_real_robot.sh
```

如果你还没装好 WebRTC 相关依赖，至少要额外确认：

- `unitree_webrtc_connect` 已安装到当前 Python 环境
- `unitree_control` 使用的 `robot_ip` 和 `connection_method` 配置正确
- 机器人和处理机网络连通

### 方案 B：Legacy / Plan B

只有在默认 WebRTC 控制链不可用，或者你明确要走旧桥接方案时，再使用：

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment
source /opt/ros/jazzy/setup.bash
source install/setup.bash
./system_real_robot.sh
```

然后另开一个终端启动 G1 桥接：

```bash
cd /home/mhw/unitree_project/g1_ros_package
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch g1_controller cmd_vel_to_g1.launch.py
```

只要导航链路里有 `/cmd_vel` 输出，桥接节点就会把速度转发给 G1。

注意：

- 不要同时运行方案 A 和方案 B
- 两套控制后端同时在线时，排查问题会非常困难
- 只有在你确认默认 `unitree_webrtc_ros` 方案不可用时，再切到 Plan B

## 最常查的文件

主导航 README：

- [README.md](/home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment/README.md)

G1 默认实机 README：

- [README.md](/home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment-unitree_g1/README.md)

G1 默认实机部署说明：

- [G1_DEPLOYMENT_GUIDE.md](/home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment-unitree_g1/G1_DEPLOYMENT_GUIDE.md)

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

- 你当前用的是方案 A 还是方案 B
- 如果是方案 A：
  - `unitree_webrtc_ros` 是否已启动
  - `~/unitree_venv` 是否已激活
  - `unitree_webrtc_connect` 是否已安装
  - `robot_ip` 和 `connection_method` 是否正确
- 如果是方案 B：
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

如果你现在主要在做通用导航和 SLAM，优先从这里开始：

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment
```

如果你现在主要在做 G1 默认实机链路，优先从这里开始：

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment-unitree_g1
```

如果你现在主要在调 G1 备用桥接，优先从这里开始：

```bash
cd /home/mhw/unitree_project/g1_ros_package
```



slam漂移问题：
先看 3 个最关键的

静止时会不会漂
让机器人完全不动 20 到 30 秒，看 /state_estimation 和 map -> sensor 是否还在慢慢走。
当前 /state_estimation 是 IMU 预积分节点直接发的，见 imuPreintegration.cpp (line 57)。
如果静止都漂，先别调规划，优先查 IMU、时间同步、外参。

IMU 和雷达时间有没有对齐
重点看：

/imu/data 频率稳不稳
/lidar/scan 频率稳不稳
header 时间戳有没有跳变、倒退、明显延迟
IMU 到 LiDAR 外参对不对
这个文件里旋转现在是单位阵，见 livox_mid360_calibration.yaml (line 4)。
如果真机安装时 IMU 和 Mid-360 不是严格同姿态，这里很容易导致漂。

然后重点看配置

use_imu_roll_pitch 现在是关的
见 livox_mid360.yaml (line 30)、livox_mid360.yaml (line 71)、livox_mid360.yaml (line 117)。
如果漂移主要表现为俯仰/横滚估计不稳，这里值得重点怀疑。

IMU 加速度限幅可能太紧
见 livox_mid360.yaml (line 122)。
现在是：

x: 0.3
y: 0.2
z: 0.1
对真机运动来说，这组值偏保守。
如果是“静止基本还行，一动就飘”，我会优先怀疑这里。

真机上常见但容易忽略的

传感器安装是否松动
Mid-360 或 IMU 支架有轻微振动，都会让轨迹发散。

TF/坐标系是否一致
检查 map / sensor / imu 的方向定义有没有和实际安装反掉。

雷达数据质量
看点云有没有明显丢包、卡顿、视场遮挡、网卡抖动。

起步方式
建议先原地静止建图，再低速直线，再小半径转弯。
一上来快转、快走，最容易把问题放大。

明天如果还漂，最值得留给我 4 样东西

30 秒静止 bag
话题至少录：
/imu/data
/lidar/scan
/tf
/state_estimation
一小段低速直线 bag
传感器安装照片
尤其是 IMU 和 Mid-360 相对姿态
你当时用的这两个配置文件
livox_mid360.yaml
livox_mid360_calibration.yaml