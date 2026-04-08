# Unitree G1 自主导航系统 - 输入输出分析

本文档详细说明了该项目的输入输出架构，包括传感器输入、控制输出以及各模块之间的数据流。

---

## 📥 系统输入（Inputs）

### 1. 传感器输入

#### 1.1 激光雷达（Livox Mid-360）

**话题名称**：`/livox/lidar`（原始数据）→ `/registered_scan`（配准后）

**消息类型**：
- 原始：`livox_ros_driver2/CustomMsg` 或 `sensor_msgs/PointCloud2`
- 配准后：`sensor_msgs/PointCloud2`

**数据内容**：
- 3D 点云数据（x, y, z 坐标）
- 强度信息（反射率）
- 时间戳

**发布频率**：~10 Hz

**数据流**：
```
Livox Mid-360 硬件
    ↓
livox_ros_driver2 节点
    ↓
/livox/lidar 话题
    ↓
arise_slam_mid360 节点（SLAM）
    ↓
/registered_scan 话题（配准到全局地图坐标系）
```

**使用场景**：
- SLAM 建图与定位
- 障碍物检测
- 地形分析

---

#### 1.2 机器人位置估计（Odometry）

**话题名称**：`/state_estimation`

**消息类型**：`nav_msgs/Odometry`

**数据内容**：
```
位置 (position):
  - x, y, z：机器人在地图坐标系中的位置（米）

姿态 (orientation):
  - 四元数（x, y, z, w）：机器人的朝向

速度 (twist):
  - linear: 线速度（x, y, z 方向）
  - angular: 角速度（roll, pitch, yaw）
```

**发布频率**：~50 Hz

**来源**：SLAM 系统（arise_slam_mid360）

**使用场景**：
- 路径规划
- 控制反馈
- 地图配准

---

#### 1.3 地形分析数据

**话题名称**：`/terrain_map`

**消息类型**：`sensor_msgs/PointCloud2`

**数据内容**：
- 可通行区域点云
- 障碍物点云
- 地面高度信息

**发布频率**：~5 Hz

**来源**：`terrain_analysis` 或 `terrain_analysis_ext` 节点

**使用场景**：
- 局部路径规划
- 障碍物规避
- 可通行性评估

---

### 2. 用户输入

#### 2.1 手柄输入（Joystick）

**话题名称**：`/joy`

**消息类型**：`sensor_msgs/Joy`

**数据内容**：
```cpp
axes[]:    // 摇杆轴位置（-1.0 到 1.0）
  - axes[0]: 左摇杆 X 轴（左右平移）
  - axes[1]: 左摇杆 Y 轴（前后移动）
  - axes[2]: 右摇杆 X 轴（原地转向）
  - axes[3]: 右摇杆 Y 轴（未使用）

buttons[]: // 按键状态（0 或 1）
  - button[0]: A/Cross - 确认
  - button[1]: B/Circle - 取消
  - button[4]: LB/L1 - 降低速度
  - button[5]: RB/R1 - 提高速度
```

**发布频率**：~50 Hz（有输入时）

**使用场景**：
- 手动遥控
- 紧急停止
- 模式切换

---

#### 2.2 导航目标点（Waypoint）

**话题名称**：`/way_point`

**消息类型**：`geometry_msgs/PointStamped`

**数据内容**：
```
header:
  frame_id: "map"       // 坐标系
  stamp: <时间戳>

point:
  x: <目标 X 坐标（米）>
  y: <目标 Y 坐标（米）>
  z: <目标 Z 坐标（米，通常为 0）>
```

**发布方式**：
- RVIZ 界面点击设置
- 命令行手动发布
- 探索规划器自动生成

**使用场景**：
- 自主导航目标设置
- 路径规划起点

---

#### 2.3 探索模式控制

**话题名称**：`/exploration_start`

**消息类型**：`std_msgs/Bool`

**数据内容**：
- `true`: 开始自主探索
- `false`: 停止探索

**使用场景**：
- 启动/停止自主探索模式

---

### 3. 配置输入

#### 3.1 机器人配置文件

**路径**：`src/base_autonomy/local_planner/config/unitree/unitree_g1.yaml`

**关键参数**：
```yaml
localPlanner:
  ros__parameters:
    maxSpeed: 0.75           # 最大速度（m/s）
    autonomySpeed: 0.75      # 自主导航速度
    goalReachedThreshold: 0.3 # 目标到达阈值
    goalClearRange: 0.6      # 目标安全区域

pathFollower:
  ros__parameters:
    maxAccel: 1.5            # 最大加速度
    maxYawRate: 40.0         # 最大转向速度（deg/s）
```

---

#### 3.2 SLAM 配置文件

**路径**：`src/slam/arise_slam_mid360/config/livox_mid360.yaml`

**关键参数**：
```yaml
feature_extraction_node:
  ros__parameters:
    blindFront: 0.2          # 前方盲区
    blindBack: -0.2          # 后方盲区
    blindLeft: 0.3           # 左侧盲区
    blindRight: -0.3         # 右侧盲区
    blindDiskRadius: 0.5     # 圆柱盲区半径
```

---

## 📤 系统输出（Outputs）

### 1. 控制输出

#### 1.1 速度命令（主要输出）

**话题名称**：`/cmd_vel`

**消息类型**：`geometry_msgs/TwistStamped`

**数据内容**：
```
header:
  stamp: <时间戳>
  frame_id: "sensor"

twist:
  linear:
    x: <前后速度（m/s）>   // 正：前进，负：后退
    y: <左右速度（m/s）>   // 正：右移，负：左移（全向移动机器人）
    z: 0.0                 // 通常为 0

  angular:
    x: 0.0                 // 通常为 0
    y: 0.0                 // 通常为 0
    z: <旋转速度（rad/s）> // 正：左转，负：右转
```

**发布频率**：~20 Hz

**生成节点**：`pathFollower` 节点

**数据流**：
```
localPlanner 节点
    ↓（计算最佳路径）
pathFollower 节点
    ↓（路径跟踪 + PID 控制）
/cmd_vel 话题
    ↓
unitree_webrtc_ros 节点（WebRTC 通信）
    ↓
Unitree G1 机器人（执行运动）
```

**控制逻辑**：
- **自主模式**：根据规划路径自动计算速度
- **手动模式**：根据手柄输入直接控制
- **避障**：检测到障碍物时自动减速或停止

---

#### 1.2 WebRTC 运动命令

**内部接口**：`unitree_webrtc_connect` Python 库

**数据格式**：
```python
# 方法1：Sport Command 模式
{
    "api_id": SPORT_CMD["Move"],
    "parameter": {
        "x": <前后速度>,
        "y": <左右速度>,
        "z": <旋转速度>
    }
}

# 方法2：Wireless Controller 模拟模式
{
    "lx": <左摇杆X>,  # 对应 ROS cmd_vel.linear.y
    "ly": <左摇杆Y>,  # 对应 ROS cmd_vel.linear.x
    "rx": <右摇杆X>,  # 对应 ROS cmd_vel.angular.z
    "ry": 0
}
```

**通信方式**：WebRTC DataChannel（实时、低延迟）

---

### 2. 规划输出

#### 2.1 局部路径

**话题名称**：`/local_path`

**消息类型**：`nav_msgs/Path`

**数据内容**：
```
header:
  frame_id: "map"

poses[]:  // 路径点序列
  - header: {stamp, frame_id}
    pose:
      position: {x, y, z}
      orientation: {x, y, z, w}
```

**发布频率**：~5 Hz

**使用场景**：
- RVIZ 可视化
- 下游路径跟踪器使用

---

#### 2.2 全局路径

**话题名称**：`/global_path`

**消息类型**：`nav_msgs/Path`

**使用场景**：
- 长距离导航
- 探索规划

---

#### 2.3 探索路径

**话题名称**：`/exploration_path`

**消息类型**：`nav_msgs/Path`

**来源**：`tare_planner` 节点（探索规划器）

**使用场景**：
- 自主探索未知区域

---

### 3. 地图输出

#### 3.1 实时地图

**话题名称**：`/map`

**消息类型**：`nav_msgs/OccupancyGrid`

**数据内容**：
```
header:
  frame_id: "map"

info:
  resolution: 0.1        # 分辨率（米/栅格）
  width: <宽度>
  height: <高度>
  origin: {x, y, z}      # 地图原点

data[]:                  # 占用概率
  - -1: 未知
  - 0: 可通行
  - 100: 障碍物
```

**发布频率**：~1 Hz

**来源**：SLAM 系统

**使用场景**：
- RVIZ 可视化
- 全局路径规划
- 地图保存

---

#### 3.2 点云地图

**话题名称**：`/registered_scan`

**消息类型**：`sensor_msgs/PointCloud2`

**使用场景**：
- 高精度地图构建
- 3D 可视化

---

### 4. 状态输出

#### 4.1 到达目标状态

**话题名称**：`/goal_reached`

**消息类型**：`std_msgs/Bool`

**数据内容**：
- `true`: 已到达目标
- `false`: 未到达

---

#### 4.2 探索完成状态

**话题名称**：`/exploration_finish`

**消息类型**：`std_msgs/Bool`

**使用场景**：
- 探索模式完成通知

---

### 5. 可视化输出（用于 RVIZ）

#### 5.1 TF 变换树

**发布的坐标系**：
- `map`: 全局地图坐标系（原点）
- `odom`: 里程计坐标系
- `sensor`: 传感器坐标系（机器人中心）
- `sensor_at_scan`: 扫描时刻传感器位置
- `livox_frame`: 激光雷达坐标系

**变换关系**：
```
map
 ├─ odom
 │   └─ sensor
 │       └─ livox_frame
 └─ sensor_at_scan
```

---

#### 5.2 可视化标记

**话题名称**：
- `/path_marker`: 路径可视化
- `/obstacle_marker`: 障碍物可视化
- `/goal_marker`: 目标点可视化

**消息类型**：`visualization_msgs/Marker` 或 `MarkerArray`

---

## 🔄 数据流总览

```
┌─────────────────────────────────────────────────────────────────┐
│                        传感器输入层                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
    ┌──────────────┬──────────────────┬──────────────┐
    │              │                  │              │
[Livox Mid-360]  [IMU]         [手柄/用户输入]    [目标点]
    │              │                  │              │
/livox/lidar   (内置SLAM)          /joy          /way_point
    │              │                  │              │
    └──────────────┴──────────────────┴──────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         感知处理层                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┴─────────────────────┐
        │                                           │
[arise_slam_mid360]                        [terrain_analysis]
        │                                           │
   /registered_scan                            /terrain_map
   /state_estimation                                │
        │                                           │
        └─────────────────────┬─────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         规划决策层                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┴─────────────────────┐
        │                                           │
  [localPlanner]                            [tare_planner]
        │                                    (探索规划器)
   /local_path                                      │
        │                                    /global_path
        └─────────────────────┬─────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         控制执行层                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                      [pathFollower]
                              ↓
                         /cmd_vel
                              ↓
                  [unitree_webrtc_ros]
                              ↓
                    WebRTC DataChannel
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Unitree G1 机器人                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 关键数据接口汇总

### 输入接口

| 话题名称 | 消息类型 | 频率 | 来源 | 用途 |
|---------|---------|------|------|-----|
| `/livox/lidar` | PointCloud2 | 10Hz | Livox Mid-360 | 原始点云 |
| `/registered_scan` | PointCloud2 | 10Hz | SLAM | 配准点云 |
| `/state_estimation` | Odometry | 50Hz | SLAM | 机器人位姿 |
| `/terrain_map` | PointCloud2 | 5Hz | Terrain Analysis | 地形信息 |
| `/joy` | Joy | 50Hz | 手柄 | 遥控输入 |
| `/way_point` | PointStamped | 事件触发 | 用户/RVIZ | 导航目标 |

### 输出接口

| 话题名称 | 消息类型 | 频率 | 目标 | 用途 |
|---------|---------|------|------|-----|
| `/cmd_vel` | TwistStamped | 20Hz | WebRTC → G1 | 速度控制 |
| `/local_path` | Path | 5Hz | 可视化 | 局部路径 |
| `/global_path` | Path | 1Hz | 可视化 | 全局路径 |
| `/map` | OccupancyGrid | 1Hz | 可视化/规划 | 占用栅格地图 |

---

## 🧩 模块输入输出详解

### Local Planner（局部规划器）

**输入**：
- `/registered_scan`: 障碍物点云
- `/terrain_map`: 地形分析结果
- `/state_estimation`: 当前位姿
- `/way_point`: 目标点
- `/joy`: 手柄输入（手动模式）

**输出**：
- `/local_path`: 局部路径（给 pathFollower）
- `/cmd_vel`: 速度命令（手动模式直接输出）

---

### Path Follower（路径跟踪器）

**输入**：
- `/local_path`: 待跟踪路径
- `/state_estimation`: 当前位姿
- `/joy`: 手柄输入（手动优先）

**输出**：
- `/cmd_vel`: 速度控制命令

**控制算法**：
- 纯跟踪控制（Pure Pursuit）
- PID 速度控制
- 动态窗口法（DWA）避障

---

### SLAM（arise_slam_mid360）

**输入**：
- `/livox/lidar`: 原始激光雷达数据

**输出**：
- `/registered_scan`: 配准到地图的点云
- `/state_estimation`: 位姿估计
- `/map`: 占用栅格地图
- TF 变换：`map` → `odom` → `sensor`

---

### Unitree WebRTC ROS（机器人通信）

**输入**：
- `/cmd_vel`: ROS 速度命令

**输出**：
- WebRTC 数据通道 → G1 机器人底层控制器

**提供服务**：
- `/standup`: 站立
- `/liedown`: 趴下
- `/hello`: 挥手
- `/stretch`: 伸展
- `/recovery_stand`: 恢复站立

---

## 🎯 使用示例

### 1. 查看实时输入

```bash
# 查看激光雷达点云
ROS_DOMAIN_ID=1 ros2 topic echo /registered_scan --no-arr

# 查看机器人位置
ROS_DOMAIN_ID=1 ros2 topic echo /state_estimation

# 查看手柄输入
ROS_DOMAIN_ID=1 ros2 topic echo /joy
```

---

### 2. 手动发送控制输出

```bash
# 发送速度命令（前进 0.5 m/s）
ROS_DOMAIN_ID=1 ros2 topic pub /cmd_vel geometry_msgs/msg/TwistStamped \
  "{twist: {linear: {x: 0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}}"

# 发送目标点（地图坐标系）
ROS_DOMAIN_ID=1 ros2 topic pub /way_point geometry_msgs/msg/PointStamped \
  "{header: {frame_id: 'map'}, point: {x: 2.0, y: 1.0, z: 0.0}}" --once
```

---

### 3. 监控数据流

```bash
# 查看所有活动话题
ROS_DOMAIN_ID=1 ros2 topic list

# 查看话题发布频率
ROS_DOMAIN_ID=1 ros2 topic hz /cmd_vel
ROS_DOMAIN_ID=1 ros2 topic hz /registered_scan

# 查看话题详细信息
ROS_DOMAIN_ID=1 ros2 topic info /cmd_vel
```

---

## 🔧 调试与故障排查

### 检查输入是否正常

```bash
# 检查激光雷达
ROS_DOMAIN_ID=1 ros2 topic hz /livox/lidar
# 期望：~10 Hz

# 检查 SLAM 输出
ROS_DOMAIN_ID=1 ros2 topic hz /state_estimation
# 期望：~50 Hz

# 检查地形分析
ROS_DOMAIN_ID=1 ros2 topic hz /terrain_map
# 期望：~5 Hz
```

---

### 检查输出是否发送

```bash
# 检查速度命令
ROS_DOMAIN_ID=1 ros2 topic echo /cmd_vel
# 应该看到实时更新的速度值

# 检查 WebRTC 连接
ROS_DOMAIN_ID=1 ros2 node list | grep unitree
# 应该看到：/unitree_control

# 测试机器人响应
ROS_DOMAIN_ID=1 ros2 service call /standup std_srvs/srv/Trigger
```

---

## 📝 总结

### 核心输入

1. **Livox Mid-360** → 环境 3D 点云
2. **SLAM 系统** → 机器人位姿估计
3. **用户/RVIZ** → 导航目标点
4. **手柄** → 手动控制输入

### 核心输出

1. **`/cmd_vel`** → 速度控制命令（最终输出）
2. **`/local_path`** → 规划路径
3. **`/map`** → 实时地图
4. **WebRTC** → 与 G1 通信

### 数据流方向

```
传感器 → 感知 → 规划 → 控制 → 执行
输入   → 处理 → 决策 → 输出 → 运动
```

---

**文档版本**：1.0  
**最后更新**：2026-01-03  
**项目路径**：`/home/mhw/g1/End2end-ObjectNav-Physical-Experiment-unitree_g1`
