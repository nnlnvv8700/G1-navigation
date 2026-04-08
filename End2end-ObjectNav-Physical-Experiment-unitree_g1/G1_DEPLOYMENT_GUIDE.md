# Unitree G1 机器人部署指南

本指南详细说明如何将自主导航系统部署到 Unitree G1 人形机器人上。

---

## 🎓 新手入门：机载电脑使用指南

### 💡 什么是机载电脑？

**简单来说**：
- G1 机器人的**脑袋里**装了一台小电脑（就像笔记本电脑的主机）
- 这台电脑**没有屏幕、没有键盘、没有鼠标**
- 但它**一直在 G1 身上运行**，控制 G1 的所有动作
- 你需要用**你自己的电脑**去"远程操作"它

**工作原理图**：
```
你的电脑（有屏幕） ←→ WiFi ←→ G1 里的小电脑（没屏幕）
    ↓                              ↓
  看到画面                    真正干活的
  发送命令                    控制机器人
```

### 📝 小白完整操作流程

#### 第一步：确保你的电脑和 G1 在同一个 WiFi

**🔍 检查方法：**

1. **找到 G1 的 WiFi 热点**
   - G1 开机后，会发出一个 WiFi 信号
   - 名字通常是：`Unitree_G1_XXXX` 或类似
   - 密码：查看 G1 说明书或机身标签

2. **用你的电脑连接这个 WiFi**
   - Windows: 右下角 WiFi 图标 → 找到 Unitree_G1_XXX → 输入密码连接
   - Mac: 右上角 WiFi 图标 → 找到 Unitree_G1_XXX → 输入密码连接
   - Linux: 网络设置 → 找到 Unitree_G1_XXX → 输入密码连接

#### 第二步：找到 G1 的 IP 地址

G1 机载电脑的 IP 地址通常是：`192.168.123.161` 或 `192.168.12.1`

**🧪 测试是否能连上：**
```bash
# 在你的电脑上打开终端，输入：
ping 192.168.123.161

# 如果看到类似这样的输出，说明连通了：
# 64 bytes from 192.168.123.161: icmp_seq=1 ttl=64 time=2.5 ms

# 如果不通，试试另一个 IP：
ping 192.168.12.1
```

#### 第三步：SSH 连接到 G1（远程登录）

**SSH 是什么？**
- 就是"远程登录"的意思
- 你在自己电脑的终端里打字，实际上是在控制 G1 里的电脑

**🔐 连接步骤：**

```bash
# 在你的电脑终端输入：
ssh unitree@192.168.123.161

# 然后会提示输入密码（密码通常是）：
# 123  或  unitree  或  8876（取决于你的 G1 版本）

# 密码输入时不会显示，输入完按回车
```

**✅ 连接成功的标志：**
```bash
# 终端提示符会变成：
unitree@unitree-g1:~$
# ↑ 这说明你现在在 G1 的电脑里了！
```

#### 第四步到第六步：详细部署流程

**接下来的步骤比较专业**，涉及安装、编译、配置等操作。

👉 **详细步骤请看下面的"第一步到第四步"正式部署指南**，包括：
- 📦 **第一步**：在 G1 上安装 ROS 2 和依赖包
- 📥 **第一步**：传输项目并编译（约 10-15 分钟）
- 🔌 **第二步**：配置激光雷达和 WebRTC 通信
- ⚙️ **第三步**：调整参数（重要！盲区配置）
- 🚀 **第四步**：启动系统

> **💡 新手提示**：下面的正式指南会一步步教你完成所有配置。不要跳过任何步骤，特别是**第二步和第三步的配置**！

### 🎯 每次使用 G1 的快速流程

**首次部署后**，之后每次使用 G1 只需要：

```
第1步：开启 G1 机器人电源 ⚡
  ↓
第2步：你的电脑连接 G1 的 WiFi 📶
  ↓
第3步：SSH 登录 G1 🔐
      命令：ssh unitree@192.168.123.161
  ↓
第4步：激活虚拟环境并启动系统 🚀
      命令：source ~/unitree_venv/bin/activate
            cd ~/g1_autonomy_ws/End2end-ObjectNav-Physical-Experiment-unitree_g1
            export ROBOT_CONFIG_PATH="unitree/unitree_g1"
            ./system_real_robot.sh
  ↓
第5步：在你的电脑上启动 RVIZ 监控 🖥️
      命令：export ROS_DOMAIN_ID=1
            ros2 run rviz2 rviz2
  ↓
第6步：在 RVIZ 里设置目标点，G1 开始自主导航！ 🎉
```

> **📌 重要**：第4步的路径是 `~/g1_autonomy_ws`（这是正式部署时使用的工作空间路径）

### ❓ 新手常见问题

#### Q1: 找不到 G1 的 WiFi 怎么办？
**A**: 
1. 确保 G1 已开机（至少等 2-3 分钟）
2. 检查 G1 机身上的 LED 指示灯
3. 试试用手机搜索 WiFi，看是否能找到
4. 查看 G1 说明书确认 WiFi 名称

#### Q2: ping 不通 G1 怎么办？
**A**:
```bash
# 试试扫描网络，找到 G1 的真实 IP
# Linux/Mac:
arp -a | grep unitree

# 或者用 nmap 扫描（需要先安装）
nmap -sn 192.168.123.0/24
```

#### Q3: SSH 连接时密码不对？
**A**: 常见密码列表（依次尝试）：
- `123`
- `unitree`
- `8876`
- `unitree123`

#### Q4: 忘记自己在哪台电脑上了？
**A**: 看终端提示符：
```bash
mhw@nnlnvv:~$          # 这是你自己的电脑
unitree@unitree-g1:~$  # 这是 G1 的电脑
```

### 💡 小贴士

1. **保持两个终端窗口打开**：
   - 终端1：SSH 连接到 G1（运行程序）
   - 终端2：你的电脑（查看 RVIZ）

2. **如果 G1 卡住了**：
   - 在 SSH 终端按 `Ctrl+C` 停止程序
   - 物理按下 G1 的急停按钮

3. **传输文件很慢？**
   - 用 USB 线连接可能更快
   - 或者只传必要的代码，不要传 build 文件夹

---

## 📋 部署前准备

### 硬件要求

#### 必需硬件
- ✅ **Unitree G1 机器人**
- ✅ **Livox Mid-360 激光雷达** - 用于 SLAM 和环境感知
- ✅ **机载计算机**（已安装在 G1 上）
  - Ubuntu 24.04
  - ROS 2 Jazzy
  - 至少 16GB RAM
  - 推荐：Intel i7 或更高，或 NVIDIA Jetson Orin

#### 可选硬件
- 🎮 PS3/PS4/Xbox 手柄 - 用于手动控制
- 📡 WiFi 路由器 - 用于远程监控

### 软件要求

- Ubuntu 24.04 LTS
- ROS 2 Jazzy
- Python 3.10+
- 相关依赖库（PCL、Eigen、OpenCV 等）

---


---

## 🔧 第一步：系统安装

### 1.1 安装 ROS 2 Jazzy

在 G1 的机载计算机上执行：

```bash
# 设置 sources
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# 添加 ROS 2 仓库
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# 安装 ROS 2 Jazzy
sudo apt update
sudo apt upgrade
sudo apt install ros-jazzy-desktop-full

# 配置环境
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 1.2 安装依赖包

```bash
sudo apt update
sudo apt install -y \
  ros-jazzy-pcl-ros \
  libpcl-dev \
  git \
  python3-pip \
  python3-colcon-common-extensions \
  libeigen3-dev \
  libopencv-dev \
  ros-jazzy-tf2-ros \
  ros-jazzy-tf2-geometry-msgs \
  ros-jazzy-serial
```

### 1.3 克隆项目到 G1

```bash
# 在 G1 上创建工作空间
cd ~
mkdir -p ~/g1_autonomy_ws
cd ~/g1_autonomy_ws

# 克隆项目（假设你已经在开发机上配置好）
# 方法1: 通过 git（如果项目在 git 仓库）
git clone <your-repo-url>

# 方法2: 通过 scp 从你的开发机传输（推荐）
# 在开发机（你的电脑）上打开新终端执行：

# 选项A：传输整个项目（包含所有文件，较慢）
scp -r ~/g1/End2end-ObjectNav-Physical-Experiment-unitree_g1 unitree@192.168.123.161:~/g1_autonomy_ws/
# 根据网络速度，可能需要 5-20 分钟

# 选项B：排除 build 文件夹（推荐，更快）
rsync -av --progress --exclude='build' --exclude='install' --exclude='log' \
  ~/g1/End2end-ObjectNav-Physical-Experiment-unitree_g1 \
  unitree@192.168.123.161:~/g1_autonomy_ws/
# 这样会快很多，因为不传输编译产物

# 如果 G1 的 IP 是 192.168.12.1，则替换为：
# rsync -av --progress --exclude='build' --exclude='install' --exclude='log' \
#   ~/g1/End2end-ObjectNav-Physical-Experiment-unitree_g1 \
#   unitree@192.168.12.1:~/g1_autonomy_ws/
```

**传输说明**：
- 传输过程中会提示输入密码（通常是 `123` 或 `unitree` 或 `8876`）
- 使用 `rsync` 排除 build 文件夹可以节省大量时间
- 传输完成后，会在 G1 上看到 `~/g1_autonomy_ws/End2end-ObjectNav-Physical-Experiment-unitree_g1` 目录
```

### 1.4 编译项目

```bash
cd ~/g1_autonomy_ws/End2end-ObjectNav-Physical-Experiment-unitree_g1

# 完整编译（包含 SLAM 和 Mid-360 驱动）
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

# 配置环境
source install/setup.bash
echo "source ~/g1_autonomy_ws/End2end-ObjectNav-Physical-Experiment-unitree_g1/install/setup.bash" >> ~/.bashrc
```

---

## 🔌 第二步：硬件连接与配置

### 2.1 Livox Mid-360 激光雷达连接

> **✅ 如果你的 G1 已经集成了激光雷达**（安装在头部），可以跳过物理连接部分，直接进行网络配置和软件配置。出厂集成的激光雷达通常已经完成物理安装和供电。

#### 物理连接（仅适用于需要自行安装的情况）
1. 将 Mid-360 安装在 G1 头部或背部（确保 360° 视野）
2. 通过以太网线连接 Mid-360 到机载计算机
3. 供电连接：Mid-360 需要 12-24V 电源

#### 网络配置（所有用户都需要）

##### 步骤 1：查找激光雷达 IP 地址

对于集成激光雷达的 G1，常见的默认 IP 地址：
- `192.168.1.111`
- `192.168.1.123`
- `192.168.1.161`

**测试连接**：
```bash
# 在 G1 机载电脑上测试激光雷达连接
ping 192.168.1.111
ping 192.168.1.123
ping 192.168.1.161

# 哪个能通就用哪个 IP
```

**如果以上IP都不通，尝试查找**：
```bash
# 方法1：检查 G1 官方文档或出厂配置

# 方法2：扫描网段（需要先安装 nmap）
sudo apt install nmap
sudo nmap -sn 192.168.1.0/24 | grep -B 2 -i livox

# 方法3：查看网络接口
ip addr show
# 找到连接激光雷达的网口（通常是 eth0 或 eth1），查看其网段
```

##### 步骤 2：修改配置文件

找到激光雷达IP后，修改驱动配置：

```bash
cd ~/g1_autonomy_ws/End2end-ObjectNav-Physical-Experiment-unitree_g1
nano src/utilities/livox_ros_driver2/config/MID360_config.json
```

修改 IP 地址为你找到的实际 IP：
```json
{
  "lidar_ip": "192.168.1.111",  // 改为你的 Mid-360 实际 IP
  "data_port": 6699,
  "cmd_port": 6688,
  "timestamp_type": 2
}
```

> **💡 提示**：如果你的 G1 是出厂集成版本，激光雷达 IP 通常已经由厂家配置好，可以查看 G1 的技术文档或联系售后支持获取准确的 IP 地址。

### 2.2 G1 机器人通信配置

#### 安装 unitree_webrtc_connect（必需）

Unitree G1 使用 WebRTC 进行远程控制和状态反馈。需要先安装 Python 依赖包。

**在 G1 机载电脑上执行以下步骤**：

##### 步骤 1：安装系统依赖

```bash
# 更新软件包列表
sudo apt update

# 安装必需的系统依赖
sudo apt install -y \
  python3-pip \
  python3-venv \
  portaudio19-dev
```

##### 步骤 2：创建 Python 虚拟环境

```bash
# 创建虚拟环境
python3 -m venv ~/unitree_venv

# 激活虚拟环境
source ~/unitree_venv/bin/activate

# 安装 ROS 2 依赖
pip install PyYAML
```

##### 步骤 3：安装 unitree_webrtc_connect

```bash
# 克隆 unitree_webrtc_connect 仓库
cd ~
git clone https://github.com/VectorRobotics/unitree_webrtc_connect.git

# 进入目录
cd unitree_webrtc_connect

# 安装包（需要 5-10 分钟，会下载大量依赖）
pip install -e .
```

> **⏱️ 注意**：安装过程可能需要 5-10 分钟，会下载约 70MB 的依赖包，请耐心等待。

##### 步骤 4：配置环境变量（重要！）

每次使用前需要激活虚拟环境：

```bash
# 手动激活（每次新终端都需要）
source ~/unitree_venv/bin/activate

# 或者创建便捷别名（推荐）
echo 'alias activate_unitree="source ~/unitree_venv/bin/activate"' >> ~/.bashrc
source ~/.bashrc

# 之后只需运行：
activate_unitree
```

##### 步骤 5：验证安装

```bash
# 在激活虚拟环境后测试
python3 -c "import unitree_webrtc_connect; print('✅ unitree_webrtc_connect 安装成功！')"
```

如果看到"✅ unitree_webrtc_connect 安装成功！"，说明安装正确。

#### 编译 unitree_webrtc_ros 节点

```bash
# 确保虚拟环境已激活
source ~/unitree_venv/bin/activate

# 编译 WebRTC ROS 节点
cd ~/g1_autonomy_ws/End2end-ObjectNav-Physical-Experiment-unitree_g1
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release --packages-select unitree_webrtc_ros

# 刷新环境
source install/setup.bash
```

#### 配置 G1 网络

```bash
# G1 默认 IP：192.168.12.1（通过 LocalAP 模式）
# 或通过 WiFi 连接后获取 IP

# 测试 G1 连接
ping 192.168.12.1
```

**连接方式说明**：
- **LocalAP 模式**：直接连接 G1 的 WiFi 热点（Unitree_G1_XXX），G1 IP 固定为 `192.168.12.1`
- **LocalSTA 模式**：G1 和你的电脑连接到同一个路由器，需要查找 G1 的动态 IP

##### 查找 G1 在 LocalSTA 模式下的 IP

```bash
# 方法1：在路由器管理界面查看
# 登录路由器 → 查看已连接设备 → 找到 "Unitree" 或 "G1"

# 方法2：使用 nmap 扫描
sudo apt install nmap
sudo nmap -sn 192.168.1.0/24 | grep -B 2 "Unitree"

# 方法3：检查 ARP 表
arp -a | grep -i unitree
```

---

## ⚙️ 第三步：配置参数

### 3.1 修改 Local Planner 参数

根据 G1 的实际尺寸和性能调整参数：

```bash
nano ~/g1_autonomy_ws/End2end-ObjectNav-Physical-Experiment-unitree_g1/src/base_autonomy/local_planner/config/unitree/unitree_g1.yaml
```

关键参数调整：

```yaml
localPlanner:
  ros__parameters:
    # 速度限制（初始保守设置）
    maxSpeed: 0.75          # 最高 0.75 m/s
    autonomySpeed: 0.75     # 自主导航速度

    # 目标到达阈值
    goalReachedThreshold: 0.3   # 距离目标 0.3m 算到达
    goalClearRange: 0.6         # 目标周围 0.6m 安全区域

pathFollower:
  ros__parameters:
    # 运动参数
    maxAccel: 1.5           # 最大加速度 m/s²
    maxYawRate: 40.0        # 最大转向速度 deg/s
```

### 3.2 配置 SLAM 参数（重要！）

**这是最关键的配置**，必须根据激光雷达在 G1 上的安装位置调整盲区参数。

```bash
nano ~/g1_autonomy_ws/End2end-ObjectNav-Physical-Experiment-unitree_g1/src/slam/arise_slam_mid360/config/livox_mid360.yaml
```

**对于头部集成激光雷达的 G1（推荐配置）**：
```yaml
feature_extraction_node:
  ros__parameters:
    # 激光雷达在头部，需要遮蔽 G1 的身体和手臂
    blindFront: 0.2         # 前方死角（遮蔽前方手臂）
    blindBack: -0.2         # 后方死角（遮蔽背部）
    blindLeft: 0.3          # 左侧死角（遮蔽左侧手臂）
    blindRight: -0.3        # 右侧死角（遮蔽右侧手臂）
    blindDiskLow: -0.05     # 圆柱死角下限（遮蔽头部以下）
    blindDiskHigh: 0.05     # 圆柱死角上限（遮蔽头顶）
    blindDiskRadius: 0.5    # 圆柱形死角半径（遮蔽躯干）
```

> **⚠️ 重要**：由于 G1 是人形机器人，激光雷达在头部时会扫描到自己的手臂和身体。**必须正确配置盲区**，否则 SLAM 会把自己的身体当作障碍物！

**如何验证盲区配置是否正确**：
```bash
# 启动系统后，查看点云
ROS_DOMAIN_ID=1 ros2 topic echo /registered_scan --no-arr

# 在 RVIZ 中观察点云，应该看不到 G1 自己的身体
# 如果看到身体点云，需要调大盲区参数
```

**修改后需要重新编译**：
```bash
cd ~/g1_autonomy_ws/End2end-ObjectNav-Physical-Experiment-unitree_g1
colcon build --packages-select arise_slam_mid360
source install/setup.bash
```

---

## 🚀 第四步：启动系统

### 💡 关于建图的说明

**这个系统使用在线SLAM（实时建图），有两种使用方式：**

#### 方式1：边导航边建图（推荐新手）
- ✅ **不需要预先建图**
- ✅ 启动后直接设置目标点，系统会自动导航并实时建图
- ⚠️ 初始阶段地图信息较少，导航可能较保守

#### 方式2：先手动建图再自主导航（推荐）
- ✅ **先用手动模式让 G1 走一圈**，建立初始地图
- ✅ 有了初始地图后，自主导航效果更好
- ✅ 特别适合复杂环境

**建议流程**：
```
1. 启动系统（SLAM + Local Planner）
2. 用手柄手动控制 G1 在环境中走一圈（2-3分钟）
3. 在 RVIZ 中观察地图是否完整
4. 切换到自主导航模式，设置目标点
```

> **📌 重要**：这个系统支持**增量式建图**，即使没有预先建图，在导航过程中也会不断完善地图。所以可以直接开始导航！

---

### 4.1 启动前检查清单

- [ ] G1 已开机并连接
- [ ] Mid-360 激光雷达通电且连接正常
- [ ] 机载计算机已连接到 G1 网络
- [ ] ROS 环境已配置
- [ ] 确保足够的活动空间（至少 5m x 5m）

### 4.2 基础系统启动

> **⚠️ 重要**：每次启动系统前，必须先激活 Python 虚拟环境！

```bash
# 第一步：激活虚拟环境（必需！）
source ~/unitree_venv/bin/activate
```

#### 方法 1：使用启动脚本（推荐）

```bash
cd ~/g1_autonomy_ws/End2end-ObjectNav-Physical-Experiment-unitree_g1

# 设置机器人配置
export ROBOT_CONFIG_PATH="unitree/unitree_g1"

# 启动系统
./system_real_robot.sh
```

#### 方法 2：分步启动（用于调试）

> **提示**：每个终端都需要先激活虚拟环境

**终端 1：启动 SLAM**
```bash
# 激活虚拟环境
source ~/unitree_venv/bin/activate

cd ~/g1_autonomy_ws/End2end-ObjectNav-Physical-Experiment-unitree_g1
source install/setup.bash
export ROBOT_CONFIG_PATH="unitree/unitree_g1"

ROS_DOMAIN_ID=1 ros2 launch arise_slam_mid360 arise_slam_mid360.launch
```

**终端 2：启动 Local Planner**
```bash
# 激活虚拟环境
source ~/unitree_venv/bin/activate

cd ~/g1_autonomy_ws/End2end-ObjectNav-Physical-Experiment-unitree_g1
source install/setup.bash
export ROBOT_CONFIG_PATH="unitree/unitree_g1"

ROS_DOMAIN_ID=1 ros2 launch local_planner local_planner_g1.launch
```

**终端 3：启动 RVIZ（在远程基站）**
```bash
# 在你的远程监控电脑上
export ROS_DOMAIN_ID=1
ros2 run rviz2 rviz2 -d <path_to_rviz_config>
```

### 4.3 启动 WebRTC 遥控（可选）

如果需要使用手柄通过 WebRTC 控制：

```bash
# 激活虚拟环境（重要！）
source ~/unitree_venv/bin/activate

# 在 G1 上的另一个终端
cd ~/g1_autonomy_ws/End2end-ObjectNav-Physical-Experiment-unitree_g1
source install/setup.bash

ROS_DOMAIN_ID=1 ros2 launch unitree_webrtc_ros unitree_control.launch.py \
  robot_ip:=192.168.12.1 \
  connection_method:=LocalAP
```

**参数说明**：
- `robot_ip`: G1 的 IP 地址（LocalAP 模式固定为 192.168.12.1）
- `connection_method`: 连接方式
  - `LocalAP`: 直接连接 G1 的 WiFi（推荐）
  - `LocalSTA`: G1 和电脑都连接到同一路由器
- `control_mode`: 控制模式（可选）
  - `sport_cmd`: 运动命令模式（默认，推荐）
  - `wireless_controller`: 无线手柄模拟模式

---

## 🧪 第五步：测试与验证

### 5.0 手动建图（新手推荐）

**为什么要手动建图**：虽然系统支持边导航边建图，但手动建一次初始地图可以：
- ✅ 让你熟悉环境和系统
- ✅ 获得更完整准确的初始地图
- ✅ 提高后续自主导航的成功率

---

#### 📋 准备清单

**在开始建图前，确保以下条件满足**：

1. **系统已完全启动**
```bash
# 在 G1 上，确认以下节点都在运行：
ROS_DOMAIN_ID=1 ros2 node list

# 应该看到：
# /livox_driver (雷达驱动)
# /arise_slam_node (SLAM 节点)
# /localPlanner (局部规划器)
# /terrainAnalysis (地形分析)
# /sport_mode_cmd_node (WebRTC 控制节点)
```

2. **手柄已连接并配对**
```bash
# 在 PC 上打开 RVIZ 后，按下手柄任意按键测试连接
# 观察终端是否有手柄输入信息
```

3. **G1 站立稳定**
   - 确保机器人已经站起来
   - 身体姿态平稳（不晃动）
   - 双脚平放在地面上

4. **环境已准备**
   - 地面平坦无障碍
   - 光线充足（虽然 LiDAR 不需要光线，但你需要看清楚环境）
   - 周围至少 2 米空间没有障碍物

---

#### 🎮 步骤 1：熟悉手柄操作

**手柄布局**（以 Xbox/PlayStation 风格为例）：

```
左摇杆（Left Stick）：
  ↑ ↓ : 前进/后退
  ← → : 左右平移

右摇杆（Right Stick）：
  ← → : 原地转向（Yaw）

按键：
  LB/L1 : 降低速度档位
  RB/R1 : 提高速度档位
  Start : 站立模式
  Select: 阻尼模式（紧急情况使用）
```

**先原地测试**：
```bash
# 1. 轻推左摇杆 ↑，让 G1 缓慢前进 0.5 米
# 2. 松开摇杆，G1 应该停下
# 3. 轻推右摇杆 →，让 G1 原地右转 30 度
# 4. 轻推左摇杆 ←，让 G1 左平移 0.3 米

# ⚠️ 注意：开始时摇杆幅度要小，熟练后再加大
```

---

#### 🗺️ 步骤 2：开始建图

**2.1 打开 RVIZ 观察界面**

在你的 PC 上：
```bash
cd ~/g1_autonomy_ws
source install/setup.bash
ROS_DOMAIN_ID=1 rviz2 -d src/base_autonomy/vehicle_simulator/rviz/g1_navigation.rviz
```

**需要显示的关键信息**：
- ✅ **PointCloud2** (`/registered_scan`)：雷达扫描点云（彩色点）
- ✅ **Map** (`/map`)：正在构建的地图（灰色栅格）
- ✅ **TF**：机器人的位置和姿态（红绿蓝坐标轴）
- ✅ **Path** (`/local_path`)：局部规划路径（黄色线）

**2.2 选择建图路线**

推荐的建图路线策略：

```
方案 A - 沿墙绕圈（适合矩形房间）：
┌─────────────────┐
│  ④ ←←←←←← ③    │
│  ↓         ↑    │
│  ↓         ↑    │
│  ① →→→→→→ ②    │
└─────────────────┘
起点：① 房间一角
路线：沿着墙壁顺时针或逆时针走一圈

方案 B - 之字形扫描（适合大空间）：
→→→→→→→→→→
         ↓
←←←←←←←←←←
↓
→→→→→→→→→→
覆盖整个区域，就像除草机一样
```

**2.3 执行建图**

**第一阶段 - 起始定位（30 秒）**：
```bash
# 1. 让 G1 站在起点，原地慢慢旋转 360 度
# 操作：右摇杆轻推 → 保持，旋转一圈后松开
# 目的：让 SLAM 观察周围环境，建立初始地图

# 2. 在 RVIZ 中观察：
# - 点云（白色或彩色点）应该形成周围环境的轮廓
# - Map 开始出现灰色区域（已知空间）
# - 黑色区域是障碍物
# - 白色区域是可通行区域
```

**第二阶段 - 慢速行走（2-3 分钟）**：
```bash
# 建图要领：
# 1. 速度：0.3-0.5 m/s（慢走）
#    - 太快：SLAM 来不及处理，地图会模糊
#    - 太慢：效率低，但不会影响质量

# 2. 运动方式：
#    ✅ 平滑的直线运动
#    ✅ 缓慢的转向（每秒 < 30 度）
#    ✅ 在角落稍作停顿（1-2 秒）
#    ❌ 避免急转弯
#    ❌ 避免后退（除非必要）
#    ❌ 避免原地快速旋转

# 3. 关注点：
#    - 墙角：停留 1-2 秒，让雷达看清楚
#    - 门口：慢速通过，确保两侧墙壁都扫描到
#    - 狭窄通道：更慢速通过（0.2 m/s）
#    - 开阔区域：可以稍快（0.5 m/s）

# 4. 实时监控 RVIZ：
#    - 地图在不断扩展（灰色区域增加）
#    - 墙壁边缘清晰（不是一团模糊）
#    - 没有重影（同一面墙不会出现两次）
```

**具体操作示例**（沿墙绕圈）：
```bash
# 阶段 1：从起点向前走 3 米
左摇杆 ↑ 推到 30% → 数 6 秒 → 松开

# 阶段 2：右转 90 度
右摇杆 → 推到 20% → 慢慢转到面向新方向 → 松开

# 阶段 3：继续前进 3 米
左摇杆 ↑ 推到 30% → 数 6 秒 → 松开

# 阶段 4：再次右转 90 度
右摇杆 → 推到 20% → 慢慢转到面向新方向 → 松开

# 重复以上步骤，直到走完一圈回到起点附近
```

---

#### 🔍 步骤 3：检查地图质量

**3.1 视觉检查（在 RVIZ 中）**

**好的地图特征**：
```
✅ 墙壁：
   - 边缘清晰，厚度均匀（1-2 个栅格宽）
   - 直线墙壁是直的，不是波浪形
   - 拐角处清晰，不是圆弧

✅ 空间：
   - 可通行区域显示为白色或浅灰色
   - 障碍物显示为黑色
   - 未探索区域显示为深灰色（正常）

✅ 闭环：
   - 如果绕了一圈，起点和终点应该重合
   - 没有明显的地图"裂缝"或错位
```

**不好的地图特征**：
```
❌ 重影：同一面墙出现两次（说明定位漂移）
❌ 模糊：墙壁边缘厚度 > 3 个栅格（说明速度太快或运动不平稳）
❌ 扭曲：明明是矩形房间，地图却是歪的（说明 SLAM 失败）
❌ 空洞：明明走过的区域却显示未探索（说明雷达盲区或数据丢失）
```

**3.2 数据检查（命令行）**

```bash
# 在 PC 上检查地图话题
ROS_DOMAIN_ID=1 ros2 topic hz /map
# 期望输出：平均 1-2 Hz（地图更新频率）

# 检查地图信息
ROS_DOMAIN_ID=1 ros2 topic echo /map --once | head -n 20
# 查看：
# - width/height：地图尺寸（应该 > 100）
# - resolution：分辨率（通常 0.1 米/栅格）

# 检查 SLAM 定位状态
ROS_DOMAIN_ID=1 ros2 topic echo /odometry --once
# 查看：
# - position: x, y, z（机器人位置）
# - orientation: 应该有合理的四元数值
```

**3.3 质量评分标准**

| 评分 | 特征 | 建议 |
|------|------|------|
| 🌟🌟🌟🌟🌟 优秀 | 墙壁清晰，无重影，闭环完美 | 可以开始自主导航 |
| 🌟🌟🌟🌟 良好 | 墙壁清晰，略有模糊，闭环基本吻合 | 可以导航，建议后续优化 |
| 🌟🌟🌟 一般 | 墙壁可辨认，有轻微重影 | 建议重新建图 |
| 🌟🌟 较差 | 墙壁模糊，重影明显 | 必须重新建图，检查参数 |
| 🌟 失败 | 地图完全错乱 | 检查硬件连接和配置 |

---

#### 💾 步骤 4：保存地图（可选）

虽然系统使用在线 SLAM（地图会持续更新），但保存地图有以下好处：
- 📋 记录初始探索成果
- 🔄 下次启动可以快速重定位
- 📊 对比前后地图变化

**保存方法**：

```bash
# 方法 1：在 G1 上保存
ssh unitree@<G1_IP>
cd ~/g1_autonomy_ws
source install/setup.bash
ROS_DOMAIN_ID=1 ros2 run nav2_map_server map_saver_cli -f maps/my_room_$(date +%Y%m%d_%H%M)

# 会生成：
# maps/my_room_20260102_1430.pgm  (地图图像)
# maps/my_room_20260102_1430.yaml (地图元数据)

# 方法 2：在 PC 上保存（推荐）
cd ~/g1_autonomy_ws
mkdir -p maps
ROS_DOMAIN_ID=1 ros2 run nav2_map_server map_saver_cli -f maps/my_room_$(date +%Y%m%d_%H%M)
```

**查看保存的地图**：
```bash
# 使用图像查看器
eog maps/my_room_20260102_1430.pgm
# 或
gimp maps/my_room_20260102_1430.pgm
```

---

#### ❓ 常见问题

**Q1：建图过程中 RVIZ 没有显示地图？**
```bash
# 检查话题连接
ROS_DOMAIN_ID=1 ros2 topic list | grep map
# 应该看到 /map

ROS_DOMAIN_ID=1 ros2 topic hz /map
# 应该有更新频率

# 如果没有，检查 G1 上的 SLAM 节点
ssh unitree@<G1_IP>
ROS_DOMAIN_ID=1 ros2 node list | grep slam
```

**Q2：地图一直有重影，怎么办？**
```bash
# 原因可能是：
# 1. 运动速度太快 → 降低到 0.2-0.3 m/s
# 2. 雷达盲区参数不正确 → 检查 livox_mid360.yaml
# 3. 地面反射太多 → 调整 blindDiskRadius 参数
```

**Q3：建图时 G1 突然停止或摇晃？**
```bash
# 可能原因：
# 1. 手柄连接断开 → 重新配对手柄
# 2. 局部规划器检测到碰撞风险 → 正常，重新规划即可
# 3. WebRTC 连接中断 → 检查网络，重启 WebRTC 节点
```

**Q4：地图边界外有很多噪点？**
```bash
# 正常现象，可以忽略
# 这些是雷达扫到远处物体的反射
# 不影响导航，因为规划器只关注机器人周围的地图
```

**Q5：建图后多久地图会过期？**
```bash
# 在线 SLAM 的地图永远不会过期
# 系统会持续更新地图：
# - 新出现的障碍物会被添加
# - 移除的障碍物会逐渐淡出
# - 建议每周手动检查一次地图质量
```

---

#### 📝 建图完成后

建图完成后，你可以：

1. **立即开始自主导航**：参见 5.2 节
2. **优化地图质量**：再走一圈，重点优化模糊区域
3. **保存地图**：使用上述保存方法

> **💡 小贴士**：第一次建图可能需要 5-8 分钟，不要着急。熟练后 2-3 分钟就能建立高质量地图。

---

### 5.1 基础功能测试

#### 测试 1：激光雷达数据
```bash
# 检查激光点云话题
ROS_DOMAIN_ID=1 ros2 topic list | grep scan

# 查看点云数据
ROS_DOMAIN_ID=1 ros2 topic echo /registered_scan --no-arr
```

#### 测试 2：SLAM 定位
```bash
# 查看机器人位置估计
ROS_DOMAIN_ID=1 ros2 topic echo /state_estimation

# 应该看到实时更新的位置和姿态信息
```

#### 测试 3：地形分析
```bash
# 检查地形图话题
ROS_DOMAIN_ID=1 ros2 topic echo /terrain_map --no-arr
```

### 5.2 手动控制测试（Smart Joystick 模式）

1. 在 RVIZ 中观察机器人周围环境
2. 使用手柄右摇杆轻微推动
3. 观察 G1 是否响应并自动避障
4. **注意**：初次测试时保持低速，准备随时按急停

### 5.3 路点导航测试

1. 在 RVIZ 中点击 "Waypoint" 按钮
2. 在机器人前方 2-3 米处点击设置路点
3. 观察 G1 是否自动导航到目标
4. 检查避障行为是否正常

### 5.4 通过命令行测试导航

```bash
# 发送路点（距离当前位置 2 米前方）
ROS_DOMAIN_ID=1 ros2 topic pub /way_point geometry_msgs/msg/PointStamped \
  '{header: {frame_id: "map"}, point: {x: 2.0, y: 0.0, z: 0.0}}' --once

# 观察 G1 是否开始移动
```

---

## 🔍 第六步：常见问题排查

### 问题 1：G1 不移动

**可能原因**：
- G1 的安全锁未解除
- WebRTC 连接未建立
- 速度指令未正确发送

**解决方案**：
```bash
# 1. 检查 cmd_vel 话题
ROS_DOMAIN_ID=1 ros2 topic echo /cmd_vel

# 2. 检查 G1 状态
ROS_DOMAIN_ID=1 ros2 topic echo /robot_state

# 3. 确保 WebRTC 正常运行
ROS_DOMAIN_ID=1 ros2 node list | grep webrtc
```

### 问题 2：激光雷达无数据

**解决方案**：
```bash
# 1. 检查网络连接
ping 192.168.1.123

# 2. 重启激光雷达驱动
ROS_DOMAIN_ID=1 ros2 launch livox_ros_driver2 msg_MID360_launch.py

# 3. 检查 USB/以太网线缆
```

### 问题 3：unitree_webrtc_connect 相关问题

#### 问题 3.1：ModuleNotFoundError: No module named 'unitree_webrtc_connect'

**原因**：忘记激活虚拟环境

**解决方案**：
```bash
# 激活虚拟环境
source ~/unitree_venv/bin/activate

# 验证安装
python3 -c "import unitree_webrtc_connect; print('OK')"
```

#### 问题 3.2：WebRTC 连接失败

**解决方案**：
```bash
# 1. 检查 G1 网络连接
ping 192.168.12.1

# 2. 确认 G1 的 IP 地址
# LocalAP 模式：192.168.12.1（固定）
# LocalSTA 模式：需要查找动态 IP

# 3. 检查 WebRTC 节点是否运行
ROS_DOMAIN_ID=1 ros2 node list | grep unitree

# 4. 查看错误日志
ROS_DOMAIN_ID=1 ros2 topic echo /rosout
```

#### 问题 3.3：依赖包安装失败

**常见错误**：`error: externally-managed-environment`

**解决方案**：
```bash
# 使用虚拟环境（推荐）
python3 -m venv ~/unitree_venv
source ~/unitree_venv/bin/activate
pip install -e ~/unitree_webrtc_connect

# 或使用 --break-system-packages（不推荐）
pip install -e ~/unitree_webrtc_connect --break-system-packages
```

### 问题 4：SLAM 漂移严重

**解决方案**：
- 降低移动速度：修改 `autonomySpeed` 参数
- 增加环境特征：在环境中添加更多可识别物体
- 调整 SLAM 参数：增加特征提取阈值

### 问题 5：机器人震荡或卡住

**解决方案**：
```yaml
# 修改 local_planner 参数
goalReachedThreshold: 0.5    # 增大到达阈值
goalClearRange: 0.8          # 增大安全距离
maxAccel: 1.0                # 降低加速度
```

---

## 📊 第七步：性能优化

### 7.1 速度优化

经过初步测试后，可以逐步提高速度：

```yaml
# unitree_g1.yaml
localPlanner:
  ros__parameters:
    maxSpeed: 1.0              # 从 0.75 增加到 1.0
    autonomySpeed: 0.9

pathFollower:
  ros__parameters:
    maxAccel: 2.0              # 从 1.5 增加到 2.0
    maxYawRate: 60.0           # 从 40.0 增加到 60.0
```

### 7.2 调整避障灵敏度

```yaml
localPlanner:
  ros__parameters:
    obstacleHeightThre: 0.15   # 增加高度阈值，更敏感
    adjacentRange: 4.5         # 增加感知范围
```

### 7.3 优化导航精度

```yaml
localPlanner:
  ros__parameters:
    goalReachedThreshold: 0.2  # 减小到达阈值，更精确
    goalClearRange: 0.4
```

---

## 🔐 第八步：安全注意事项

### 必须遵守的安全规则

1. ⚠️ **首次测试必须在空旷区域进行**，至少 10m x 10m 无障碍空间
2. ⚠️ **始终有人准备按下 G1 的急停按钮**
3. ⚠️ **初始速度设置为保守值**（0.5 m/s 以下）
4. ⚠️ **避免在人员密集区域测试**
5. ⚠️ **定期检查激光雷达和传感器状态**
6. ⚠️ **G1 电量低于 20% 时停止测试**

### 紧急停止方法

- **方法 1**：按下 G1 机身上的急停按钮
- **方法 2**：在终端按 Ctrl+C 停止程序
- **方法 3**：发送停止命令：
  ```bash
  ROS_DOMAIN_ID=1 ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
    '{linear: {x: 0, y: 0, z: 0}, angular: {x: 0, y: 0, z: 0}}'
  ```

---

## 📝 第九步：启动脚本模板

创建方便的启动脚本：

### start_g1_autonomy.sh
```bash
#!/bin/bash

echo "======================================"
echo "启动 Unitree G1 自主导航系统"
echo "======================================"

# 激活虚拟环境（重要！）
echo "激活 Python 虚拟环境..."
source ~/unitree_venv/bin/activate

# 设置环境
cd ~/g1_autonomy_ws/End2end-ObjectNav-Physical-Experiment-unitree_g1
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROBOT_CONFIG_PATH="unitree/unitree_g1"
export ROS_DOMAIN_ID=1

# 清理旧进程
echo "清理旧进程..."
sudo pkill -9 -f 'ros2|rviz2' 2>/dev/null
sleep 2

# 检查激光雷达连接
echo "检查激光雷达连接..."
if ping -c 1 -W 1 192.168.1.111 &> /dev/null || \
   ping -c 1 -W 1 192.168.1.123 &> /dev/null || \
   ping -c 1 -W 1 192.168.1.161 &> /dev/null; then
    echo "✓ 激光雷达连接正常"
else
    echo "✗ 警告：无法连接到激光雷达"
    echo "  尝试的 IP: 192.168.1.111, 192.168.1.123, 192.168.1.161"
    read -p "是否继续？(y/n): " choice
    if [ "$choice" != "y" ]; then
        exit 1
    fi
fi

# 检查 G1 连接
echo "检查 G1 机器人连接..."
if ping -c 1 -W 1 192.168.12.1 &> /dev/null; then
    echo "✓ G1 机器人连接正常"
else
    echo "✗ 警告：无法连接到 G1 (192.168.12.1)"
fi

# 检查 unitree_webrtc_connect
echo "检查 unitree_webrtc_connect..."
if python3 -c "import unitree_webrtc_connect" 2>/dev/null; then
    echo "✓ unitree_webrtc_connect 已安装"
else
    echo "✗ 错误：unitree_webrtc_connect 未安装或虚拟环境未激活"
    exit 1
fi

echo ""
echo "======================================"
echo "启动自主导航系统..."
echo "======================================"

# 启动系统
./system_real_robot.sh
```

### 使用方法
```bash
chmod +x ~/g1_autonomy_ws/End2end-ObjectNav-Physical-Experiment-unitree_g1/start_g1_autonomy.sh
~/g1_autonomy_ws/End2end-ObjectNav-Physical-Experiment-unitree_g1/start_g1_autonomy.sh
```

---

## 🎯 第十步：进阶功能

### 启动路由规划器
```bash
export ROBOT_CONFIG_PATH="unitree/unitree_g1"
./system_real_robot_with_route_planner.sh
```

### 启动自主探索
```bash
export ROBOT_CONFIG_PATH="unitree/unitree_g1"
./system_real_robot_with_exploration_planner.sh
```

---

## 📖 附录：完整配置文件位置

- **G1 配置**：`src/base_autonomy/local_planner/config/unitree/unitree_g1.yaml`
- **SLAM 配置**：`src/slam/arise_slam_mid360/config/livox_mid360.yaml`
- **激光雷达配置**：`src/utilities/livox_ros_driver2/config/MID360_config.json`
- **启动文件**：`src/base_autonomy/vehicle_simulator/launch/system_real_robot.launch`

---

## 🆘 技术支持

- CMU 探索实验室网站：[https://www.cmu-exploration.com](https://www.cmu-exploration.com)
- FAR Planner：[https://github.com/MichaelFYang/far_planner](https://github.com/MichaelFYang/far_planner)
- Unitree 官方文档：[https://www.unitree.com](https://www.unitree.com)

---

## ✅ 部署检查清单

使用此清单确保部署完整：

- [ ] Ubuntu 24.04 + ROS 2 Jazzy 已安装
- [ ] 项目已克隆并成功编译
- [ ] Livox Mid-360 连接并配置正确
- [ ] G1 网络连接正常
- [ ] 配置文件已根据实际情况修改
- [ ] 激光雷达数据正常发布
- [ ] SLAM 定位正常工作
- [ ] 手动控制测试通过
- [ ] 路点导航测试通过
- [ ] 避障功能测试通过
- [ ] 安全措施已到位

**祝你部署成功！🎉**
