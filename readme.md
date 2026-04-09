# G1 操作步骤

这份文档按当前已经验证过的 `G1` 现场流程整理，默认使用：

- 导航工作空间：`/home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment-unitree_g1`
- 速度桥接：`/home/mhw/unitree_project/g1_ros_package`
- 控制链：
  `/way_point -> /path -> /cmd_vel -> cmd_vel_to_g1 -> g1_loco_client -> G1`

## 1. 首次编译（运存小最好单线程编译）

### 1.1 编译 G1 导航工作空间

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment-unitree_g1
source /opt/ros/jazzy/setup.bash

colcon build --executor sequential --parallel-workers 1 --symlink-install \
  --cmake-args -DCMAKE_BUILD_TYPE=Release
```

如果只想重编 `SLAM` 相关包：

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment-unitree_g1
source /opt/ros/jazzy/setup.bash

colcon build --executor sequential --parallel-workers 1 --symlink-install \
  --cmake-args -DCMAKE_BUILD_TYPE=Release \
  --packages-select arise_slam_mid360 arise_slam_mid360_msgs
```

如果只想重编 `Livox` 驱动：

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment-unitree_g1
source /opt/ros/jazzy/setup.bash

colcon build --executor sequential --parallel-workers 1 --symlink-install \
  --cmake-args -DCMAKE_BUILD_TYPE=Release \
  --packages-select livox_ros_driver2
```

### 1.2 编译 G1 桥接工作空间

```bash
cd /home/mhw/unitree_project/g1_ros_package
source /opt/ros/jazzy/setup.bash

colcon build --executor sequential --parallel-workers 1 --symlink-install \
  --packages-select g1_controller
```

## 2. 每次启动前先清旧进程

每次重新上车前都先清，避免：

- 地图重影
- 点云/TF 叠层
- 旧的 `localPlanner`、`pathFollower`、`livox`、`cmd_vel_to_g1` 干扰新实例

```bash
pkill -f "ros2 launch vehicle_simulator system_real_robot.launch" || true
pkill -f "ros2 launch vehicle_simulator system_real_robot_g1_bridge.launch.py" || true
pkill -f "livox_ros_driver2_node" || true
pkill -f "feature_extraction_node" || true
pkill -f "imu_preintegration_node" || true
pkill -f "laser_mapping_node" || true
pkill -f "localPlanner" || true
pkill -f "pathFollower" || true
pkill -f "terrainAnalysis" || true
pkill -f "terrainAnalysisExt" || true
pkill -f "sensorScanGeneration" || true
pkill -f "visualizationTools" || true
pkill -f "cmd_vel_to_g1" || true
pkill -f "unitree_control" || true
```

## 3. 机器人切到可运动态

点位导航前，先让 `G1` 进入常规运控模式。（直接用遥控器，遥控器不能用就用下面的代码）

```bash
export LD_LIBRARY_PATH=/home/mhw/robot_g1/unitree_sdk2/thirdparty/lib/x86_64:$LD_LIBRARY_PATH

/home/mhw/robot_g1/unitree_sdk2/build/bin/g1_loco_client --network_interface=enp108s0 --set_fsm_id=1
sleep 1
/home/mhw/robot_g1/unitree_sdk2/build/bin/g1_loco_client --network_interface=enp108s0 --set_fsm_id=4
sleep 2

/home/mhw/robot_g1/unitree_sdk2/build/bin/g1_loco_client --network_interface=enp108s0 --get_fsm_id
/home/mhw/robot_g1/unitree_sdk2/build/bin/g1_loco_client --network_interface=enp108s0 --get_fsm_mode
```

如果 `4` 不工作，再试：

```bash
/home/mhw/robot_g1/unitree_sdk2/build/bin/g1_loco_client --network_interface=enp108s0 --set_fsm_id=500
```

## 4. 启动导航主链

终端 1：

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment-unitree_g1

conda deactivate 2>/dev/null || true
source ~/unitree_venv/bin/activate
source /opt/ros/jazzy/setup.bash
source install/local_setup.bash

export ROBOT_CONFIG_PATH=unitree/unitree_g1
export ROS_DOMAIN_ID=1

./system_real_robot.sh --rviz
```

## 5. 启动 G1 速度桥接

终端 2：

```bash
cd /home/mhw/unitree_project/g1_ros_package

source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=1
export LD_LIBRARY_PATH=/home/mhw/robot_g1/unitree_sdk2/thirdparty/lib/x86_64:$LD_LIBRARY_PATH

ros2 launch g1_controller cmd_vel_to_g1.launch.py \
  network_interface:=enp108s0 \
  g1_loco_client_path:=/home/mhw/robot_g1/unitree_sdk2/build/bin/g1_loco_client \
  unitree_sdk_lib_path:=/home/mhw/robot_g1/unitree_sdk2/thirdparty/lib/x86_64
```

## 6. 打开自动导航模式

终端 3：

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment-unitree_g1

source /opt/ros/jazzy/setup.bash
source install/local_setup.bash
export ROS_DOMAIN_ID=1

ros2 param set /localPlanner autonomyMode true
ros2 param set /pathFollower autonomyMode true
```

## 7. 正常点位导航

如果当前场景正常，直接在 `RViz` 里点目标点即可。

检查规划和速度：

```bash
ros2 topic echo /path --once
ros2 topic echo /cmd_vel --once
```

正常现象：

- `/path` 是一串路径点
- `/cmd_vel` 是非零速度

## 8. 点位设了但不动

适用症状：

- `RViz` 里已经设置了目标点
- `/path` 只有一个原点 `(0,0,0)`
- `/cmd_vel` 全 0

当前现场里，已经验证可走的临时处理方式是：

```bash
source /opt/ros/jazzy/setup.bash
source /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment-unitree_g1/install/local_setup.bash
export ROS_DOMAIN_ID=1

ros2 param set /localPlanner autonomyMode true
ros2 param set /pathFollower autonomyMode true
ros2 topic pub --once /check_obstacle std_msgs/msg/Bool "{data: false}"
ros2 topic pub --once /way_point geometry_msgs/msg/PointStamped "{header: {frame_id: 'map'}, point: {x: 1.0, y: 0.0, z: 0.0}}"
```

再检查：

```bash
ros2 topic echo /path --once
ros2 topic echo /cmd_vel --once
```

如果恢复正常，通常会看到：

- `/path` 不再只有原点
- `/cmd_vel` 变成非零速度

注意：

- `/check_obstacle=false` 是当前现场的临时运行方案，不是最终安全配置
- 测试时前方必须保持空场
- 后续如果要恢复更安全的状态，需要继续调整：
  - `checkObstacle`
  - `useTerrainAnalysis`
  - `obstacleHeightThre`
  - `pointPerPathThre`

## 9. 常用检查命令

### 9.1 检查节点

```bash
source /opt/ros/jazzy/setup.bash
source /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment-unitree_g1/install/local_setup.bash
export ROS_DOMAIN_ID=1

ros2 node list | rg "localPlanner|pathFollower|cmd_vel_to_g1|livox|imu_preintegration|laser_mapping"
```

### 9.2 检查关键话题

```bash
ros2 topic list | rg "imu|lidar|state_estimation|way_point|path|cmd_vel"
```

### 9.3 检查桥接是否订到 `/cmd_vel`

```bash
ros2 topic info /cmd_vel -v
```

正常应该看到：

- publisher: `pathFollower`
- subscription: `cmd_vel_to_g1`

## 10. 静止 30 秒录包

用于检查 `SLAM` 是否漂移。

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment-unitree_g1
source /opt/ros/jazzy/setup.bash
source install/local_setup.bash
export ROS_DOMAIN_ID=1

mkdir -p ~/bags
rm -rf ~/bags/g1_slam_static_30s_check

timeout 30s ros2 bag record \
  -o ~/bags/g1_slam_static_30s_check \
  /imu/data \
  /lidar/scan \
  /tf \
  /tf_static \
  /state_estimation
```

查看包信息：

```bash
ros2 bag info ~/bags/g1_slam_static_30s_check
```

## 11. 分析静止包

```bash
cd /home/mhw/unitree_project/End2end-ObjectNav-Physical-Experiment-unitree_g1
source /opt/ros/jazzy/setup.bash
source install/local_setup.bash

/usr/bin/python3 tools/analyze_g1_slam_bag.py /home/mhw/bags/g1_slam_static_30s_check
```

当前已经验证过的一次正常静止结果大致是：

- `endpoint_drift = 0.032 m`
- `speed_avg = 0.014 m/s`
- `speed_max = 0.041 m/s`

如果结果明显大很多，就说明当前运行态可能又脏了，或者 `SLAM` 状态不稳定。

## 12. 现场判断顺序

如果机器人不动，按这个顺序查：

1. `G1` 是否已经切到可运动态
2. `localPlanner` 和 `pathFollower` 的 `autonomyMode` 是否为 `true`
3. `/path` 是不是只有原点
4. `/cmd_vel` 是不是全 0
5. `cmd_vel_to_g1` 是否存在并订到了 `/cmd_vel`
6. 必要时临时执行 `/check_obstacle=false`

如果地图重影或 `SLAM` 明显异常，优先查：

1. 旧进程有没有杀干净
2. 当前是不是只用了 `unitree_g1` 这套工作空间
3. 是否用了 `install/local_setup.bash`
