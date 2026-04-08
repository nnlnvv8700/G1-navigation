# Unitree G1 实际话题分析（基于真实机器人）

> **重要说明**：本文档基于 G1 机器人实际运行时的话题列表，与理论文档可能有差异。

---

## 📡 实际话题分类

### 1. 📥 传感器输入（实际）

#### 1.1 激光雷达 Livox Mid-360

**实际话题名称**：
- `/utlidar/cloud_livox_mid360` - 点云数据
- `/utlidar/imu_livox_mid360` - IMU 数据
- `/utlidar/range_info` - 距离信息

**消息类型**：
- `sensor_msgs/PointCloud2` (点云)
- `sensor_msgs/Imu` (IMU)

**⚠️ 注意**：实际话题名不是 `/livox/lidar` 或 `/registered_scan`！

---

#### 1.2 机器人状态（IMU + Odometry）

**实际话题名称**：
- `/dog_imu_raw` - 原始 IMU 数据
- `/secondary_imu` 或 `/lf/secondary_imu` - 次级 IMU
- `/dog_odom` - 里程计数据
- `/lowstate_doubleimu` - 双 IMU 低层状态

**运动状态相关**：
- `/sportmodestate` 或 `/lf/sportmodestate` - 运动模式状态
- `/odommodestate` 或 `/lf/odommodestate` - 里程计模式状态
- `/lowstate` 或 `/lf/lowstate` - 底层状态（关节角度、力矩等）

---

#### 1.3 SLAM 定位数据

**SLAM 建图模式**：
- `/unitree/slam_mapping/odom` - SLAM 建图时的位姿
- `/unitree/slam_mapping/points` - SLAM 建图点云

**SLAM 重定位模式**：
- `/unitree/slam_relocation/odom` - 重定位时的位姿
- `/unitree/slam_relocation/points` - 重定位点云
- `/unitree/slam_relocation/global_map` - 全局地图

**SLAM 信息**：
- `/slam_info` - SLAM 状态信息
- `/slam_key_info` - SLAM 关键信息

---

#### 1.4 地图与环境感知

**地图话题**：
- `/global_map` - 全局地图
- `/planner_map` - 规划器地图
- `/gridmap` - 栅格地图

**点云分类**（用于避障）：
- `/safe_clouds` - 安全区域点云
- `/warning_clouds` - 警告区域点云
- `/collision_clouds` - 碰撞危险点云
- `/pre_collision_clouds` - 预碰撞点云
- `/pre_safe_clouds` - 预安全点云
- `/no_warning_clouds` - 无警告点云
- `/ele_clouds` - 高程点云
- `/grid_clouds` - 栅格点云

---

#### 1.5 电池与系统状态

- `/lf/bmsstate` - 电池管理系统状态
- `/lf/battery_alarm` - 电池告警
- `/lf/mainboardstate` - 主板状态
- `/multiplestate` - 多重状态

---

### 2. 📤 控制输出（实际）

#### 2.1 运动控制命令

**主要控制话题**：
- `/lowcmd` - **底层控制命令**（关节级别）
- `/loco_sdk` - **运动SDK控制**
- `/wirelesscontroller` - **无线手柄控制**

**⚠️ 重要发现**：
- **没有 `/cmd_vel` 话题！**
- G1 不使用标准的 ROS Twist 消息
- 需要通过 **API 服务**或**专用 SDK** 发送控制命令

---

#### 2.2 API 服务接口（核心控制方式）

**运动控制 API**：
```
/api/sport/request  → 运动模式请求
/api/sport/response → 运动模式响应

/api/loco/request   → 运动控制请求
/api/loco/response  → 运动控制响应
```

**常用动作 API**：
```
/api/gesture/request → 手势/姿态控制
/api/arm/request     → 手臂控制
/api/arm/response

/api/motion_switcher/request  → 运动模式切换
/api/motion_switcher/response
```

**SLAM 控制**：
```
/api/slam_operate/request  → SLAM 操作（启动/停止建图等）
/api/slam_operate/response
```

**机器人状态查询**：
```
/api/robot_state/request
/api/robot_state/response
/api/robot_type_service/request
/api/robot_type_service/response
```

---

#### 2.3 其他控制接口

**手臂控制**：
- `/arm_sdk` - 手臂 SDK 控制
- `/armsdk` - 备用手臂接口
- `/arm/action/state` - 手臂动作状态

**灵巧手控制（Dex3）**：
- `/dex3/left/cmd` - 左手控制命令
- `/dex3/left/state` - 左手状态
- `/dex3/right/cmd` - 右手控制命令
- `/dex3/right/state` - 右手状态
- `/lf/dex3/left/state` - 低频左手状态
- `/lf/dex3/right/state` - 低频右手状态

---

### 3. 🗣️ 高级功能接口

#### 3.1 语音与 GPT

```
/api/gpt/request     → GPT 请求
/api/gpt/response    → GPT 响应
/gpt_cmd             → GPT 命令
/gpt_state           → GPT 状态
/gptflowfeedback     → GPT 流程反馈

/api/voice/request   → 语音请求
/api/voice/response  → 语音响应
/api/audiohub/request  → 音频中心
/api/audiohub/response
/audio_msg           → 音频消息
/audio_msg/filter    → 音频过滤
/audiosender         → 音频发送器
```

---

#### 3.2 视频与 WebRTC

```
/api/videohub/request   → 视频中心请求
/api/videohub/response
/frontvideostream       → 前置视频流
/webrtcreq              → WebRTC 请求
/webrtcres              → WebRTC 响应
/rtc/state              → RTC 状态
/rtc_status             → RTC 状态详情
```

---

#### 3.3 配置与日志

```
/api/config/request   → 配置请求
/api/config/response
/config_change_status → 配置变更状态

/log_system_inbound   → 系统日志输入
/log_system_outbound  → 系统日志输出

/rosout               → ROS 日志
/parameter_events     → 参数事件
```

---

### 4. 🎯 导航与路径规划

**路点**：
- `/unitree_slam/waypoints` - SLAM 路点

**⚠️ 注意**：没有发现 `/way_point` 话题，可能需要：
1. 通过 API 服务发送目标
2. 或使用 `/unitree_slam/waypoints`

---

### 5. 其他话题

```
/SymState                → 符号状态
/servicestate            → 服务状态
/servicestateactivate    → 服务状态激活
/selftest                → 自检
/public_network_status   → 公共网络状态
```

---

## 🔄 实际数据流（G1 真实架构）

```
┌───────────────────────────────────────────────────────────┐
│                     硬件传感器层                             │
└───────────────────────────────────────────────────────────┘
                          ↓
    ┌─────────────┬──────────────┬──────────────┐
    │             │              │              │
[Livox Mid-360] [IMU]      [关节编码器]   [相机]
    │             │              │              │
    ↓             ↓              ↓              ↓
/utlidar/cloud  /dog_imu_raw  /lowstate  /frontvideostream
    │             │              │              │
    └─────────────┴──────────────┴──────────────┘
                          ↓
┌───────────────────────────────────────────────────────────┐
│                    Unitree SLAM 系统                        │
└───────────────────────────────────────────────────────────┘
                          ↓
        /unitree/slam_mapping/odom
        /unitree/slam_mapping/points
        /global_map, /planner_map
                          ↓
┌───────────────────────────────────────────────────────────┐
│                  点云处理与地图构建                           │
└───────────────────────────────────────────────────────────┘
                          ↓
        /safe_clouds, /warning_clouds
        /collision_clouds, /gridmap
                          ↓
┌───────────────────────────────────────────────────────────┐
│                    运动规划与控制                            │
└───────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┴─────────────────┐
        │                                   │
   [API Services]                    [Direct Control]
        │                                   │
   /api/sport/request              /lowcmd, /loco_sdk
   /api/loco/request               /wirelesscontroller
        │                                   │
        └─────────────────┬─────────────────┘
                          ↓
┌───────────────────────────────────────────────────────────┐
│                  Unitree G1 底层控制器                       │
└───────────────────────────────────────────────────────────┘
                          ↓
                    [电机执行运动]
```

---

## 🚀 如何控制 G1 机器人

### 方法 1：使用 API 服务（推荐）

```bash
# 查询机器人状态
ros2 service call /api/robot_state/request <消息类型> '{...}'

# 发送运动命令
ros2 service call /api/sport/request <消息类型> '{
  "x": 0.5,    # 前后速度
  "y": 0.0,    # 左右速度
  "yaw": 0.0   # 旋转速度
}'

# 控制 SLAM
ros2 service call /api/slam_operate/request <消息类型> '{
  "command": "start_mapping"  # 或 stop_mapping, start_relocation 等
}'
```

---

### 方法 2：使用话题发布（高频控制）

```bash
# 通过 loco_sdk 发送控制命令
ros2 topic pub /loco_sdk <消息类型> '{...}'

# 通过无线手柄模拟
ros2 topic pub /wirelesscontroller <消息类型> '{...}'

# 底层命令（需要了解具体消息格式）
ros2 topic pub /lowcmd <消息类型> '{...}'
```

---

### 方法 3：使用 unitree_webrtc_ros（需适配）

由于 G1 没有标准的 `/cmd_vel` 话题，`unitree_webrtc_ros` 节点需要修改为：
- 订阅 `/cmd_vel`（自定义导航系统发布）
- 转换为 `/api/sport/request` 或 `/loco_sdk` 格式
- 发送到 G1

---

## 🔧 集成自定义导航系统的方案

### 方案 A：创建适配层节点

创建一个 ROS 2 节点 `g1_adapter`：

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
# 导入 G1 的消息类型（需要从 unitree_sdk 获取）

class G1Adapter(Node):
    def __init__(self):
        super().__init__('g1_adapter')
        
        # 订阅标准 cmd_vel
        self.cmd_vel_sub = self.create_subscription(
            TwistStamped,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )
        
        # 发布到 G1 的控制话题
        self.loco_pub = self.create_publisher(
            <G1消息类型>,
            '/loco_sdk',
            10
        )
    
    def cmd_vel_callback(self, msg):
        # 转换 TwistStamped → G1 控制格式
        g1_cmd = <G1消息类型>()
        g1_cmd.x = msg.twist.linear.x
        g1_cmd.y = msg.twist.linear.y
        g1_cmd.yaw = msg.twist.angular.z
        
        self.loco_pub.publish(g1_cmd)
```

---

### 方案 B：修改 pathFollower 直接发布

修改 `pathFollower.cpp`：

```cpp
// 不发布到 /cmd_vel
// 改为发布到 /loco_sdk 或调用 /api/sport/request 服务

auto loco_pub = nh->create_publisher<unitree_g1_msgs::LocomotionCmd>(
    "/loco_sdk", 10
);

// 在控制循环中
unitree_g1_msgs::LocomotionCmd loco_cmd;
loco_cmd.x = vehicleSpeed * cos(dirDiff);
loco_cmd.y = vehicleSpeed * sin(dirDiff);
loco_cmd.yaw = vehicleYawRate;
loco_pub->publish(loco_cmd);
```

---

### 方案 C：使用 API 服务

```cpp
// 创建服务客户端
auto sport_client = nh->create_client<unitree_api::srv::Sport>(
    "/api/sport/request"
);

// 在控制循环中
auto request = std::make_shared<unitree_api::srv::Sport::Request>();
request->x = vehicleSpeed;
request->y = 0.0;
request->yaw = vehicleYawRate;

sport_client->async_send_request(request);
```

---

## 📋 需要获取的信息

为了完整集成，需要：

1. **消息类型定义**：
   ```bash
   # 查看 loco_sdk 的消息类型
   ros2 topic info /loco_sdk
   ros2 interface show <消息类型>
   
   # 查看 API 服务类型
   ros2 service type /api/sport/request
   ros2 interface show <服务类型>
   ```

2. **消息格式示例**：
   ```bash
   # 监听实际运行时的消息
   ros2 topic echo /loco_sdk
   ros2 topic echo /lowcmd
   ```

3. **Unitree SDK 文档**：
   - 查看 `unitree_ros2` 或 `unitree_sdk` 包的文档
   - 了解控制协议和消息格式

---

## 🔍 下一步调试命令

```bash
# 1. 查看关键消息类型
ros2 topic info /loco_sdk
ros2 topic info /lowcmd
ros2 topic info /wirelesscontroller

# 2. 查看 API 服务类型
ros2 service type /api/sport/request
ros2 service type /api/loco/request

# 3. 监听实际控制消息（手动控制时）
ros2 topic echo /wirelesscontroller
ros2 topic echo /loco_sdk

# 4. 查看接口定义
ros2 interface list | grep unitree
ros2 interface show <找到的接口类型>

# 5. 查看 SLAM 输出的位姿话题
ros2 topic echo /unitree/slam_mapping/odom
ros2 topic echo /dog_odom
```

---

## 📝 总结

### 关键差异

| 文档描述 | 实际话题 |
|---------|---------|
| `/livox/lidar` | `/utlidar/cloud_livox_mid360` |
| `/registered_scan` | `/unitree/slam_mapping/points` |
| `/state_estimation` | `/unitree/slam_mapping/odom` 或 `/dog_odom` |
| `/cmd_vel` | **不存在！需要用 `/loco_sdk` 或 API** |
| `/way_point` | `/unitree_slam/waypoints` (可能) |

### 核心发现

1. **G1 不使用标准 ROS 导航接口**
2. **必须通过 API 服务或专用话题控制**
3. **需要创建适配层连接自定义导航系统**
4. **Unitree 有自己的 SLAM 系统**

---

**文档版本**：1.0 (基于实际机器人)  
**最后更新**：2026-01-03  
**数据来源**：`ros2 topic list` 真实输出
