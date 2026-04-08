# 项目文档：Unitree G1 端到端自主导航系统

**项目名称**：End2end-ObjectNav-Physical-Experiment-unitree_g1  
**主要技术栈**：ROS 2 Jazzy、C++、PCL、Unity 仿真  
**支持平台**：Unitree G1、Unitree Go2、T-Bot（麦克纳姆轮平台）

## 项目概述

本项目是一个完整的机器人自主导航与探索系统，能够在未知环境中自动导航至指定目标点，并在此过程中建立地图。系统包含完整的感知、规划和控制模块，支持仿真环境测试和真实机器人部署。

系统核心能力：
- 🗺️ **SLAM 建图定位**：使用 Mid-360 激光雷达进行实时建图和定位
- 🧭 **地形分析**：分析环境可通行性，识别障碍物
- 🛤️ **路径规划**：包含局部避障、路由规划和探索规划
- 🎮 **多种操控模式**：手柄控制、自主导航、探索模式
- 📡 **仿真与实物**：完整的 Unity 仿真环境和真实机器人适配

---

## 系统架构总览

整个自主栈分为以下核心层次：

```
┌─────────────────────────────────────────────────────────────┐
│                   应用层（用户交互）                          │
│  RVIZ 可视化 | 手柄控制 | 目标点设置 | 探索模式              │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   规划层（Decision Making）                   │
│  ├─ 局部规划器（Local Planner）：实时避障和路径跟踪           │
│  ├─ 路由规划器（FAR Planner）：全局路由规划                   │
│  └─ 探索规划器（TARE Planner）：自主探索和建图               │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│               感知与分析层（Perception）                     │
│  ├─ SLAM 模块：定位和制图                                   │
│  ├─ 地形分析：可通行性评估                                   │
│  ├─ 传感器数据预处理：点云滤波和变换                         │
│  └─ 可视化工具：实时调试和监测                               │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              执行层（Hardware & Simulation）                 │
│  ├─ 车辆模拟器（Unity 引擎）：仿真测试                       │
│  ├─ 电机控制器：真实机器人控制                               │
│  └─ 遥控接口：多种输入方式支持                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 项目目录结构详解

### 📂 核心模块 (`src/base_autonomy/`)

#### 1️⃣ **local_planner** - 局部规划器和控制核心
**位置**：`src/base_autonomy/local_planner/`  
**职责**：机器人的核心控制模块，实现实时路径规划、碰撞避免和速度控制

**主要功能**：
- **实时避障**：根据激光雷达点云进行动态障碍物检测和避碰
- **路径跟踪**：使用纯追踪(Pure Pursuit)算法跟踪参考路径
- **速度规划**：根据路径曲率、障碍物距离动态调整速度
- **多种运动模式**：
  - *Smart Joystick 模式*：手柄控制 + 自动避碰
  - *Waypoint 模式*：自主导航到路点
  - *Manual 模式*：纯手柄控制，无避碰
- **串口通信**：与底层电机控制器通信

**关键配置参数**（`config/` 文件夹）：
```yaml
maxSpeed: 0.875 m/s           # 最大速度
autonomySpeed: 0.875 m/s      # 自主模式速度
vehicleLength: 0.5 m          # 车体长度
vehicleWidth: 0.5 m           # 车体宽度
obstacleHeightThre: 0.15 m    # 障碍物识别高度阈值
adjacentRange: 3.5 m          # 传感器规划范围
goalReachedThreshold: 0.3 m   # 目标点到达阈值
```

**ROS 话题**：
- 📥 输入：`/way_point`, `/goal_pose`, `/joy`, `/navigation_boundary`
- 📤 输出：`/cmd_vel`, `/path`, `/goal_reached`

---

#### 2️⃣ **terrain_analysis** - 地形分析
**位置**：`src/base_autonomy/terrain_analysis/`  
**职责**：分析环境中的可通行区域，生成地形成本图

**主要功能**：
- **点云聚类**：将激光雷达点云聚类为地面和障碍物
- **可通行性评估**：判断哪些区域机器人可以通过
- **成本图生成**：为规划器提供地形成本信息
- **地面高度估计**：检测坡度和高度变化
- **动态障碍物检测**：区分静态障碍物和动态物体

**主要输出**：
- `/terrain_map` - 局部地形成本图（点云格式）
- 用于 local_planner 的实时避障决策

---

#### 3️⃣ **terrain_analysis_ext** - 扩展地形分析
**位置**：`src/base_autonomy/terrain_analysis_ext/`  
**职责**：增强的地形分析，提供更大范围的地形成本信息

**主要改进**：
- **更大的分析范围**：超过激光雷达单次扫描范围
- **历史信息融合**：结合多帧点云进行更精确的地形评估
- **长期成本图维护**：为全局规划器提供参考

**应用场景**：配合 FAR Planner 进行全局规划

---

#### 4️⃣ **sensor_scan_generation** - 传感器数据预处理
**位置**：`src/base_autonomy/sensor_scan_generation/`  
**职责**：原始传感器数据的处理和转换

**主要功能**：
- **点云滤波**：移除噪声和异常点
- **坐标变换**：将传感器坐标系转换到机器人坐标系或地图坐标系
- **点云重采样**：调整点云密度以平衡计算和精度
- **时间同步**：确保多传感器数据的时间对齐

**处理流程**：
```
原始激光点云 → 滤波 → 坐标变换 → 重采样 → 地形分析
```

---

#### 5️⃣ **vehicle_simulator** - Unity 仿真器集成
**位置**：`src/base_autonomy/vehicle_simulator/`  
**职责**：与 Unity 仿真环境的接口和启动管理

**主要功能**：
- **Unity 环境启动**：自动启动 Unity 仿真程序
- **模拟传感器**：生成模拟的激光雷达点云
- **模拟电机控制**：接收速度指令并更新仿真世界中的机器人
- **环境配置管理**：加载不同的地图和场景
- **性能优化**：支持低配置和高配置版本的模型

**配置文件结构**：
```
mesh/
├── unity/
│   ├── environment/          # Unity 环境二进制文件
│   │   ├── Model.x86_64
│   │   ├── Model_Data/
│   │   └── UnityPlayer.so
│   ├── map.ply               # 点云格式的地图
│   ├── traversable_area.ply  # 可通行区域
│   ├── object_list.txt       # 环境中的物体列表
│   └── *.csv                 # 物体属性文件
```

---

#### 6️⃣ **visualization_tools** - 可视化工具
**位置**：`src/base_autonomy/visualization_tools/`  
**职责**：在 RVIZ 中可视化系统状态和调试信息

**主要功能**：
- **点云可视化**：显示激光雷达点云、地形图
- **路径可视化**：展示规划的路径和导航轨迹
- **信息文字显示**：实时显示速度、目标点等信息
- **动态参数调整**：通过 RVIZ 面板动态调节参数

**RVIZ 面板功能**：
- 设置 Waypoint（路点）
- 设置 Goal Point（目标点）
- 切换操作模式
- 重置地图和图表
- 控制机器人速度

---

#### 7️⃣ **waypoint_example** - 路点导航示例
**位置**：`src/base_autonomy/waypoint_example/`  
**职责**：演示如何通过 ROS 节点编程方式进行路点导航

**功能演示**：
- 发送一系列路点给机器人
- 设置导航边界（虚拟墙）
- 设置导航速度
- 监测导航状态

**使用示例**：
```bash
ros2 launch waypoint_example waypoint_example.launch
```

---

### 📂 规划模块 (`src/exploration_planner/` 和 `src/route_planner/`)

#### 8️⃣ **tare_planner** - 自主探索规划器
**位置**：`src/exploration_planner/tare_planner/`  
**类型**：全局规划 + 局部探索  
**论文背景**：TARE (Topologically-Aware Route Extraction) Planner

**核心功能**：
- **自主探索边界**：自动识别环境边界和前沿区域
- **信息增益规划**：优先探索信息增益最高的区域
- **拓扑感知**：考虑环境拓扑结构，避免陷入死胡同
- **全局建图**：建立完整的环境地图

**关键概念**：
- **前沿(Frontier)**：已知空间和未知空间的边界
- **候选点(Candidate Points)**：可以探索的下一个目标点
- **信息增益(Information Gain)**：探索某区域能获得多少新信息

**典型工作流**：
```
启动探索 → 分析当前地图 → 识别前沿 → 计算信息增益
   ↑                                    ↓
   └────── 发送探索目标给 Local Planner ←┘
```

**配置参数**：
```yaml
exploration_interval: 更新探索目标的时间间隔
frontier_threshold: 前沿识别距离阈值
viewpoint_distance: 观测点距离
max_exploration_goals: 保留的候选目标数量
```

---

#### 9️⃣ **far_planner** - 路由规划器
**位置**：`src/route_planner/far_planner/`  
**类型**：全局最优路由规划  
**论文背景**：FAR (Fast Autonomous Route) Planner

**核心功能**：
- **可见性图构建**：在未探索区域和已知自由空间之间构建通路
- **最优路径搜索**：使用 Dijkstra 或 A* 算法找到最短路径
- **动态更新**：随着环境探索逐步更新路由图
- **死胡同避免**：识别并避免不必要的死胡同探索

**关键概念**：
- **可见性图(Visibility Graph)**：节点是关键点，边是直线可通行路径
- **三维空间规划**：考虑高度维度的障碍物
- **自由空间**：机器人已确认可通行的区域

**导航过程**：
1. **已知空间导航**：使用可见性图中的已知最短路径
2. **未知空间探索**：当无已知路径时，向目标方向探索
3. **动态规划调整**：当发现新的障碍物时重新规划

**ROS 话题**：
- 📥 输入：`/way_point` (来自 RVIZ 的目标点)
- 📤 输出：`/path` (路由规划器生成的路径)

---

#### 🔟 **boundary_handler** - 边界处理器
**位置**：`src/route_planner/boundary_handler/`  
**职责**：处理环境边界和导航区域约束

**主要功能**：
- **边界检测**：识别环境的物理边界
- **边界跟踪**：沿着边界跟踪轨迹
- **导航区域限制**：只在指定区域内导航
- **虚拟墙设置**：用户可设置禁行区域

---

#### **visibility_graph_msg** - 消息定义
**位置**：`src/route_planner/visibility_graph_msg/`  
**职责**：定义可见性图的 ROS 消息格式

**包含内容**：
- 图的节点和边的定义
- 路径的消息格式
- 边界信息的表示

---

#### **graph_decoder** - 图解码器
**位置**：`src/route_planner/graph_decoder/`  
**职责**：将规划器输出的图结构解析为可执行的路径

---

### 📂 SLAM 定位建图模块 (`src/slam/`)

#### **arise_slam_mid360** - SLAM 主模块
**位置**：`src/slam/arise_slam_mid360/`  
**激光雷达**：Livox Mid-360（圆柱形 FOV）  
**算法基础**：VIO/LIO（视觉或激光惯性里程计）

**核心功能**：
- **特征提取**：从点云中提取平面和边线特征
- **前端里程计**：计算帧间运动（ICP、NDT 等）
- **后端优化**：使用 GTSAM 或 Ceres 进行位姿优化
- **闭环检测**：识别回访场景，修正漂移
- **增量建图**：维护和更新全局地图

**关键配置**（`config/livox_mid360.yaml`）：
```yaml
local_mode: false              # 定位模式：false=建图, true=定位
init_x/y/z: 0                  # 初始位置
init_yaw: 0                     # 初始方向
blindFront/Back/Left/Right: 0  # 激光死角补偿
```

---

#### **arise_slam_mid360_msgs** - SLAM 消息定义
**职责**：定义 SLAM 模块的自定义消息格式

---

#### **dependency** - 依赖库
**包含**：
- **Ceres Solver**：非线性优化库
- **GTSAM**：图优化和 SAM 库
- **Sophus**：李群/李代数库用于旋转表示

---

### 📂 工具模块 (`src/utilities/`)

#### **livox_ros_driver2** - 激光雷达驱动
**职责**：Livox Mid-360 激光雷达的 ROS 驱动

**功能**：
- 原始点云采集
- IP 配置和通信
- 点云发布

**配置文件**（`config/MID360_config.json`）：
```json
{
  "lidar_ip": "192.168.1.1xx",  // 根据激光雷达序列号配置
  "data_port": 6699,
  "cmd_port": 6688
}
```

---

#### **teleop_joy_controller** - 手柄遥控
**职责**：处理游戏手柄（PS3/PS4/Xbox）输入

**功能**：
- 读取手柄按键和摇杆输入
- 转换为 ROS `/joy` 消息
- 支持多种手柄类型

**按键映射**：
- 右摇杆：速度和转向控制
- L2/R2：模式切换和特殊功能
- 其他按键：模式选择等

---

#### **teleop_rviz_plugin** - RVIZ 控制插件
**职责**：在 RVIZ 中添加交互式控制面板

**提供功能**：
- Waypoint 按钮：设置导航目标
- 速度滑块：调整机器人速度
- 模式选择：Smart Joystick / Waypoint / Manual
- 状态显示：机器人当前状态

---

#### **waypoint_rviz_plugin** - 路点标记插件
**职责**：在 RVIZ 中可视化和设置路点

**功能**：
- 点击设置路点
- 显示路点列表
- 删除/编辑路点

---

#### **ROS-TCP-Endpoint** - ROS 网络通信
**职责**：实现 ROS 和其他系统（如 Unity）的 TCP 通信

---

#### **domain_bridge** - 域桥接
**职责**：连接不同 ROS 域，支持基站远程监控

**应用**：在远程基站查看机器人实时状态和地图

---

#### **serial** - 串口通信库
**职责**：与底层电机控制器的串口通信

**用途**：
- 发送速度指令给电机驱动器
- 接收编码器反馈
- 电机状态监控

---

## 系统数据流

### 核心感知-规划-执行循环

```
┌─────────────────────────────────────────────────────────────┐
│                      感知阶段                                │
├─────────────────────────────────────────────────────────────┤
│  激光雷达 → livox_ros_driver2                                │
│           → sensor_scan_generation (滤波、变换)              │
│           → SLAM (定位、建图)                               │
└─────────┬───────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                    分析阶段                                  │
├─────────────────────────────────────────────────────────────┤
│  terrain_analysis (地形可通行性评估)                        │
│  terrain_analysis_ext (扩展地形图)                          │
│  SLAM 输出 (/state_estimation - 机器人位置)                │
└─────────┬───────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                    规划阶段                                  │
├─────────────────────────────────────────────────────────────┤
│  用户输入（手柄/RVIZ）→ 目标点 / 路点                       │
│                        ↓                                     │
│  规划选择：                                                  │
│  ├─ Local Planner（局部避障 + 路径跟踪）[总是运行]          │
│  ├─ FAR Planner（全局路由）[目标点模式]                     │
│  └─ TARE Planner（自主探索）[探索模式]                      │
└─────────┬───────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                    控制阶段                                  │
├─────────────────────────────────────────────────────────────┤
│  local_planner 生成 /cmd_vel (速度指令)                     │
│             → serial (串口通信)                             │
│             → 电机驱动器                                     │
│             → 机器人执行运动                                 │
└─────────┬───────────────────────────────────────────────────┘
          │
          └────────────────► [反馈到下一个循环]
```

---

## 操作模式详解

### 1. 🎮 Smart Joystick 模式（智能手柄模式）
**默认模式**，机器人听从手柄指令但保持避碰

- **激活方式**：右手柄任何输入 / 按下手柄上的模式按钮
- **控制方式**：
  - 右摇杆 XY：前进速度和左右平移速度
  - 右摇杆旋转：转向角速度
- **系统行为**：试图执行手柄指令，但在障碍物面前自动停止或绕过
- **适用场景**：环境探索、遥控操控、紧急停止恢复

### 2. 📍 Waypoint 模式（路点导航模式）
**自主导航**，机器人自动前往指定路点或目标

- **激活方式**：RVIZ 中点击"Waypoint"按钮后点击地图 / 按手柄上的路点模式按钮
- **设置方式**：
  - RVIZ：交互式设置（点击要去的位置）
  - ROS 节点：发送 `/way_point` 话题
  - 手柄：按住路点模式按钮，用摇杆调整（前进速度）
- **系统行为**：
  - 自动规划避开障碍物的路径
  - 考虑地形可通行性
  - 路点应相对接近（3-5 米内），过远容易卡住
- **取消方式**：设置新路点 / 按下智能模式按钮 / 发送取消指令
- **适用场景**：精确目标导航、自主抵达指定点

### 3. 🗺️ Global Route Planning 模式（全局规划模式）
**长距离自主导航**，使用 FAR Planner 规划全局路由

- **激活方式**：启动 `system_*_with_route_planner.sh`
- **设置目标**：RVIZ 中"Goalpoint"按钮点击地图上的远距离点
- **系统行为**：
  1. FAR Planner 构建可见性图（cyan 色显示）
  2. 搜索从当前位置到目标的最短路径（green 显示已知路径，blue 显示未知探索）
  3. 在已知空间使用最优路径，在未知空间向目标探索
  4. 实时更新路由图，发现新障碍物时重新规划
- **与基础系统交互**：
  - FAR Planner 生成路点序列给 Local Planner
  - Local Planner 执行避碰和速度控制
- **适用场景**：长距离导航、大环境探索

### 4. 🔍 Exploration 模式（自主探索模式）
**完全自主**，机器人自动探索环境并建图

- **激活方式**：启动 `system_*_with_exploration_planner.sh`
- **目标设置**：可选（无目标则持续探索）
- **系统行为**：
  1. TARE Planner 识别环境前沿（已知和未知的边界）
  2. 计算探索的信息增益，选择最优前沿点
  3. 自动向前沿移动，不断扩展已知区域
  4. 避免重复探索和陷入死胡同
- **地图增长**：随着探索，地图逐步完善
- **停止条件**：
  - 手动停止
  - 达到时间限制
  - 已探索所有可访问区域
- **适用场景**：未知环境全面勘测、自主地图创建

### 5. 🚗 Manual 模式（手动模式）
**完全遥控**，无任何自主避碰

- **激活方式**：按手柄上的 Manual 按钮
- **控制方式**（Mode 2 设定）：
  - 右摇杆：前进/后退速度（XY）
  - 左摇杆：旋转角速度（Z）
- **系统行为**：完全执行指令，碰撞时会生成速度饱和但不停止
- **风险**：可能撞击障碍物
- **适用场景**：紧急调整、已知安全环境操作、测试电机

---

## 启动系统流程

### 完整启动步骤

#### 🔧 环境配置
```bash
# 1. 配置机器人型号
export ROBOT_CONFIG_PATH="unitree/unitree_g1"  # 或 "unitree/unitree_b1"、"mechanum_drive"

# 2. 进入项目目录
cd ~/g1/End2end-ObjectNav-Physical-Experiment-unitree_g1

# 3. 清除之前的 ROS 进程
sudo pkill -9 -f '/opt/ros/.*\/lib\/|\/install\/.*\/lib\/|_ros2_daemon'
```

#### 仿真模式
```bash
# 基础自主系统（无规划器）
./system_simulation.sh

# 带路由规划器
./system_simulation_with_route_planner.sh

# 带探索规划器
./system_simulation_with_exploration_planner.sh
```

#### 真实机器人
```bash
# 基础自主系统
export ROBOT_CONFIG_PATH="unitree/unitree_g1"
./system_real_robot.sh

# 进程中运行 WebRTC 遥控（另一个终端）
ros2 launch unitree_webrtc_ros unitree_control.launch.py \
  robot_ip:=192.168.12.1 connection_method:=LocalAP
```

#### 离线 Bagfile 处理
```bash
# 从保存的 ROS bagfile 回放数据
./system_bagfile_with_exploration_planner.sh
```

### 启动脚本的工作原理

脚本执行流程：
1. **加载配置**：读取 `ROBOT_CONFIG_PATH` 指定的参数文件
2. **启动 SLAM**：初始化定位和建图模块
3. **启动 Local Planner**：启动基础控制和避碰
4. **启动规划器**（可选）：根据脚本选择启动 FAR Planner 或 TARE Planner
5. **启动 RVIZ**：打开可视化界面
6. **启动驱动和工具**：激光雷达、手柄、串口等

---

## 关键配置文件说明

### Local Planner 配置
**路径**：`src/base_autonomy/local_planner/config/unitree/unitree_g1.yaml`

```yaml
# 车体参数
vehicleLength: 0.6        # 机器人长度 [m]
vehicleWidth: 0.3         # 机器人宽度 [m]

# 速度限制
maxSpeed: 1.0             # 最大速度 [m/s]
autonomySpeed: 0.6        # 自主导航速度 [m/s]
maxAccel: 2.0             # 最大加速度 [m/s²]

# 目标点容差
goalReachedThreshold: 0.3 # 到达目标的距离阈值 [m]
goalClearRange: 0.3       # 目标周围安全半径 [m]

# 传感器参数
adjacentRange: 3.5        # 规划范围 [m]
obstacleHeightThre: 0.15  # 障碍物高度阈值 [m]

# 坐标系参数
config: "omniDir"         # 麦克纳姆轮配置（"standard" 用于普通轮）
```

### SLAM 配置
**路径**：`src/slam/arise_slam_mid360/config/livox_mid360.yaml`

```yaml
local_mode: false         # false = 建图模式, true = 定位模式
init_x: 0.0              # 初始 X 坐标
init_y: 0.0              # 初始 Y 坐标
init_z: 0.0              # 初始 Z 坐标
init_yaw: 0.0            # 初始偏航角

# 激光死角（针对 Mid-360 的圆柱 FOV）
blindFront: 0.1          # 前方死角 [m]
blindBack: -0.2          # 后方死角 [m]
blindLeft: 0.1           # 左侧死角 [m]
blindRight: -0.1         # 右侧死角 [m]
```

### 激光雷达配置
**路径**：`src/utilities/livox_ros_driver2/config/MID360_config.json`

```json
{
  "lidar_ip": "192.168.1.1xx",    // xx = 激光雷达序列号最后两位
  "data_port": 6699,
  "cmd_port": 6688,
  "timestamp_type": 2
}
```

---

## ROS 消息接口

### 重要输入话题

| 话题 | 消息类型 | 说明 |
|------|---------|------|
| `/way_point` | `geometry_msgs/PointStamped` | 设置目标路点 |
| `/goal_pose` | `geometry_msgs/PoseStamped` | 设置目标点和方向 |
| `/cancel_goal` | `std_msgs/Bool` | 取消导航（data: true） |
| `/joy` | `sensor_msgs/Joy` | 手柄输入 |
| `/navigation_boundary` | `geometry_msgs/PolygonStamped` | 设置导航边界 |
| `/added_obstacles` | `sensor_msgs/PointCloud2` | 虚拟障碍物 |

### 重要输出话题

| 话题 | 消息类型 | 说明 |
|------|---------|------|
| `/state_estimation` | `nav_msgs/Odometry` | 机器人位置和速度（来自 SLAM） |
| `/registered_scan` | `sensor_msgs/PointCloud2` | 当前帧点云（地图坐标系） |
| `/terrain_map` | `sensor_msgs/PointCloud2` | 局部地形成本图 |
| `/path` | `nav_msgs/Path` | Local Planner 的路径 |
| `/cmd_vel` | `geometry_msgs/Twist` | 速度指令 |
| `/goal_reached` | `std_msgs/Bool` | 目标是否到达 |
| `/overall_map` | `sensor_msgs/PointCloud2` | 全局地图（仅仿真） |

### 发送目标示例

```bash
# 发送路点（自主导航到该点）
ros2 topic pub /way_point geometry_msgs/msg/PointStamped \
  '{header: {frame_id: "map"}, point: {x: 5.0, y: 3.0, z: 0.0}}' --once

# 发送目标点和方向
ros2 topic pub /goal_pose geometry_msgs/msg/PoseStamped \
  '{header: {frame_id: "map"}, pose: {position: {x: 5.0, y: 3.0, z: 0.0}, orientation: {w: 1.0}}}' --once

# 取消导航
ros2 topic pub /cancel_goal std_msgs/msg/Bool 'data: true' --once
```

---

## 常见故障排查

### 问题 1：机器人在目标点附近振荡
**原因**：目标容差太小或参数不匹配

**解决方案**：
```yaml
# 在 local_planner 配置中增加
goalReachedThreshold: 0.5      # 增加到 0.5 m
goalClearRange: 0.4
slowDwnDisThre: 1.0            # 增加减速距离
```

### 问题 2：激光点云抖动或缺失
**原因**：时间同步问题或激光雷达故障

**检查**：
```bash
# 查看激光点云
ros2 topic echo /scan --no-arr
# 检查激光连接
ros2 node list | grep livox
```

### 问题 3：SLAM 漂移严重
**原因**：特征不足、高速运动或地面滑动

**改进**：
- 降低速度参数 `autonomySpeed`
- 增加特征丰富的地图材质
- 检查激光雷达标定

### 问题 4：机器人被卡住无法脱困
**原因**：路径不可通行或参数过保守

**处理**：
```bash
# 切换到手动模式摆脱困境
# 手柄按 Manual 模式按钮
# 或通过 RVIZ 点击新目标重启导航
```

---

## 性能指标和优化建议

### 系统实时性

| 组件 | 处理频率 | 说明 |
|------|---------|------|
| Livox Mid-360 | 10 Hz | 点云发布频率 |
| Local Planner | 10 Hz | 避障和控制循环 |
| Terrain Analysis | 10 Hz | 地形评估频率 |
| SLAM | 10 Hz | 位姿更新频率 |
| FAR Planner | 1-2 Hz | 全局规划更新 |
| TARE Planner | 1-2 Hz | 探索目标更新 |

### 优化建议

#### 对于紧凑空间导航
```yaml
goalReachedThreshold: 0.2      # 更精确
goalClearRange: 0.25
vehicleLength: 0.5
vehicleWidth: 0.25
```

#### 对于高速导航
```yaml
autonomySpeed: 1.0             # 增加速度
lookAheadDis: 1.0              # 增加预瞄距离
maxAccel: 3.0                  # 提高加速度
```

#### 对于复杂地形
```yaml
adjacentRange: 5.0             # 扩大感知范围
obstacleHeightThre: 0.2        # 更敏感的障碍检测
```

---

## 文件树完整视图

```
.
├── AUTONOMY_STACK_README.md         # 自主栈 API 文档
├── CLAUDE.md                        # AI 助手指南
├── README.md                        # 项目主说明
├── instruction.txt                  # 使用说明
├── *.sh                             # 启动脚本（仿真/真实/规划器版本）
├── go2_sbus_control.py              # Go2 电机控制脚本
├── src/
│   ├── base_autonomy/               # 核心导航系统
│   │   ├── local_planner/           # ⭐ 主控制器
│   │   ├── terrain_analysis/        # 地形分析
│   │   ├── terrain_analysis_ext/    # 扩展地形分析
│   │   ├── sensor_scan_generation/  # 传感器预处理
│   │   ├── vehicle_simulator/       # Unity 仿真接口
│   │   ├── visualization_tools/     # RVIZ 可视化
│   │   └── waypoint_example/        # 路点导航示例
│   ├── exploration_planner/         # 自主探索
│   │   └── tare_planner/            # ⭐ TARE 探索规划器
│   ├── route_planner/               # 全局规划
│   │   ├── far_planner/             # ⭐ FAR 路由规划器
│   │   ├── boundary_handler/        # 边界处理
│   │   ├── graph_decoder/           # 图解码
│   │   └── visibility_graph_msg/    # 消息定义
│   ├── slam/                        # 定位和建图
│   │   ├── arise_slam_mid360/       # ⭐ SLAM 主模块
│   │   ├── arise_slam_mid360_msgs/  # SLAM 消息
│   │   └── dependency/              # Ceres、GTSAM 等
│   └── utilities/                   # 工具和驱动
│       ├── livox_ros_driver2/       # ⭐ Mid-360 驱动
│       ├── teleop_joy_controller/   # 手柄控制
│       ├── teleop_rviz_plugin/      # RVIZ 控制插件
│       ├── waypoint_rviz_plugin/    # 路点插件
│       ├── domain_bridge/           # 网络通信
│       ├── ROS-TCP-Endpoint/        # TCP 接口
│       ├── serial/                  # 串口通信
│       └── goalpoint_rviz_plugin/   # 目标点插件
├── desktop_buttons/                 # 桌面快捷方式
├── base_station/                    # 基站配置
├── chrony_conf/                     # 时间同步配置
└── img/                             # 文档图片
```

---

## 快速参考

### 常用启动命令

```bash
# 仿真基础系统
export ROBOT_CONFIG_PATH="mechanum_drive" && ./system_simulation.sh

# 仿真+路由规划
export ROBOT_CONFIG_PATH="mechanum_drive" && ./system_simulation_with_route_planner.sh

# 仿真+自主探索
export ROBOT_CONFIG_PATH="mechanum_drive" && ./system_simulation_with_exploration_planner.sh

# 真实 G1 机器人
export ROBOT_CONFIG_PATH="unitree/unitree_g1" && ./system_real_robot.sh
```

### 常用 ROS 命令

```bash
# 列出所有节点
ros2 node list

# 列出所有话题
ros2 topic list

# 查看话题内容
ros2 topic echo /state_estimation

# 发送路点
ros2 topic pub /way_point geometry_msgs/msg/PointStamped \
  '{header: {frame_id: "map"}, point: {x: 5.0, y: 3.0, z: 0.0}}' --once
```

---

## 总结

这是一个专业级别的机器人自主导航和探索系统，组织清晰、功能完整：

- **感知层**：通过 SLAM 和地形分析实现精确定位和环境认知
- **规划层**：支持三种规划模式（局部避障、全局路由、自主探索）
- **控制层**：多种操控模式满足不同应用需求
- **软硬件支持**：既支持仿真验证，也支持真实机器人部署

系统设计遵循模块化原则，各个组件高度解耦，易于扩展和定制。

