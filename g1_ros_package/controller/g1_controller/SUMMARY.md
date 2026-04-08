# G1 Robot Control - Issue Summary and Solutions

## Issues Identified

### 1. ✅ FIXED: Library Conflict Crash
**Error:** `free(): invalid pointer` when initializing any SDK example
**Cause:** ROS 2's iceoryx libraries conflicting with SDK libraries
**Solution:** Set `LD_LIBRARY_PATH` before running any example:
```bash
export LD_LIBRARY_PATH=/home/rey/unitree_g1_control/unitree_sdk2/thirdparty/lib/x86_64:$LD_LIBRARY_PATH
```

### 2. ✅ FIXED: Motor Error in Low-Level Control
**Error:** `[ERROR] motor X with code 1074003968` when running ankle swing
**Cause:** Commands sent before motors are ready after releasing motion services
**Solution:** Added delays and checks in the code:
- 3-second wait after releasing motion services
- Only send commands after receiving valid motor state

### 3. ✅ FIXED: Wrong Locomotion Service Name
**Error:** RPC timeout (error 3104) - locomotion service not responding
**Cause:** SDK configured for `"sport"` service (ai_sport >= 8.2.0.0), but robot runs older version using `"loco"`
**Solution:** Changed service name in `include/unitree/robot/g1/loco/g1_loco_api.hpp`:
```cpp
const std::string LOCO_SERVICE_NAME = "loco";  // Changed from "sport"
```
Then rebuilt: `cd build && make`

### 4. ✅ FIXED: Robot Not Moving Despite Accepting Commands
**Issue:** `set_velocity` commands accepted but robot doesn't move
**Cause:** Robot in FSM ID 0 (ZeroTorque) - motors are passive/off
**Solution:** Must set FSM to active state before movement:
```bash
# Set to StandUp mode (FSM ID 4) to enable movement
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --set_fsm_id=4
```

## Quick Start Guide

### For Low-Level Control (ankle swing, dual arm, etc.)

```bash
# 1. Set library path
export LD_LIBRARY_PATH=/home/rey/unitree_g1_control/unitree_sdk2/thirdparty/lib/x86_64:$LD_LIBRARY_PATH

# 2. Run your example
./build/bin/g1_ankle_swing_example enx00051bd51a1a
```

### For High-Level Control (Making Robot Walk)

```bash
# 1. Set library path
export LD_LIBRARY_PATH=/home/rey/unitree_g1_control/unitree_sdk2/thirdparty/lib/x86_64:$LD_LIBRARY_PATH

# 2. Check robot's current state
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --get_fsm_id
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --set_fsm_id=1 # We need to make the robot go to damping mode first 
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --damp # same as set_fsm_id=1

# 2.5. Stand UP 
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --set_fsm_id=4 # Must go here first before 500
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --stand_up # same as id 4

# 3. Activate the robot (set to StandUp mode - FSM ID 4)
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --set_fsm_id=500 #Have to go to 500

# 4. Now the robot can move! Send velocity commands:
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --set_velocity="0.2 0 0 3"
# Parameters: vx vy omega duration (in m/s, m/s, rad/s, seconds)

# 5. Stop the robot
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --stop_move

# 6. When done, put robot back to safe mode
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --set_fsm_id=1 # Need to go to 1 first and then 0
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --set_fsm_id=0
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --zero_torque # same as id 0

# DON'T TRY CONTINUOS GATE (CANNOT BE STOPPED)
```

# Direction
# x direction (front) - y direction (left) - yaw direction (anti-clockwise)

```bash
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --stop_move # to stop move
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --move="0 0 -0.2" # 1 tick (shorter than 1 second)


```

## Changes Made to Code

### File: `g1_ankle_swing_example.cpp`

1. **Added startup delay after releasing motion services:**
   ```cpp
   sleep(3);  // Wait for motors to transition to ready state
   ```

2. **Added motor state check in LowCommandWriter:**
   ```cpp
   const std::shared_ptr<const MotorState> ms = motor_state_buffer_.GetData();
   if (mc && ms) {  // Only send if both command and state are available
       // ... send commands
   }
   ```

This ensures commands are only sent after:
- Motion services are fully released
- Motors have transitioned to ready state
- Valid motor state data has been received

## FSM (Finite State Machine) Modes Explained

The robot uses FSM states to control its behavior. You must be in the correct FSM state for movement.

### FSM State Reference

| FSM ID | Name | Description | Use Case |
|--------|------|-------------|----------|
| **0** | ZeroTorque | Motors are passive/off | Safe idle state, no movement possible |
| **1** | Damp | Damping mode - motors provide resistance | Transition state, compliant movement |
| **2** | Squat | Robot squats down | Positional state |
| **3** | Sit | Robot sits down | Positional state |
| **4** | StandUp | **Active standing mode** | **REQUIRED for walking/movement** |
| **500** | Start | Main movement control mode | Alternative active state |

### State Transitions for Walking

**Recommended sequence:**
```bash
# 1. Start from safe state (usually already in 0)
--get_fsm_id                    # Check current state

# 2. Go to damping mode (optional, smoother transition)
--set_fsm_id=1                  # Damp mode

# 3. Activate for movement
--set_fsm_id=4                  # StandUp mode - NOW MOTORS ARE ACTIVE

# 4. Send movement commands
--set_velocity="vx vy omega duration"

# 5. Return to safe state when done
--set_fsm_id=0                  # ZeroTorque - motors off
```

### Movement Commands (Only work in FSM ID 4 or 500)

| Command | Description | Example |
|---------|-------------|---------|
| `--set_velocity` | Walk for duration | `--set_velocity="0.3 0 0 2"` (forward 0.3 m/s for 2 sec) |
| `--move` | Continuous movement | `--move="0.2 0 0"` (forward 0.2 m/s continuously) |
| `--stop_move` | Stop all movement | `--stop_move` |

**Velocity Parameters:**
- `vx`: Forward/backward velocity (m/s) - positive = forward
- `vy`: Left/right velocity (m/s) - positive = left
- `omega`: Rotation velocity (rad/s) - positive = counter-clockwise
- `duration`: How long to move (seconds) - optional for set_velocity

## Testing Status

| Example | Status | Notes |
|---------|--------|-------|
| Audio client | ✅ Works | Basic DDS/RPC communication confirmed |
| Ankle swing | ✅ Works | Low-level motor control functional |
| Loco client | ✅ Works | High-level locomotion control functional |
| Robot walking | ✅ Works | Must set FSM ID 4 first, then send velocity |

## Walking Control Examples

### Basic Forward Walk
```bash
# Activate robot
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --set_fsm_id=4

# Walk forward at 0.3 m/s for 3 seconds
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --set_velocity="0.3 0 0 3"

# Stop
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --stop_move
```

### Walk Sideways (Strafe)
```bash
# Walk left at 0.2 m/s for 2 seconds
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --set_velocity="0 0.2 0 2"
```

### Turn in Place
```bash
# Rotate counter-clockwise at 0.5 rad/s for 2 seconds
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --set_velocity="0 0 0.5 2"
```

### Combined Movement (Walk and Turn)
```bash
# Walk forward while turning
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --set_velocity="0.3 0 0.3 3"
```

### Continuous Movement (No Auto-Stop)
```bash
# Move forward continuously until stop command
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --move="0.2 0 0"

# Stop when ready
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --stop_move
```

## Important Notes

1. **Always check FSM state first:** `--get_fsm_id`
2. **Robot must be in FSM ID 4 to move** - this is the most important step!
3. **Service name matters:** Robot uses `"loco"` not `"sport"` (fixed in SDK)
4. **Network interface:** Use `enx00051bd51a1a` (your USB-Ethernet adapter)
5. **Robot IP:** 192.168.123.161 (controller), 192.168.123.164 (computer)
6. **Safety:** Always use `--stop_move` or set FSM to 0 when done

## Command Cheat Sheet

```bash
# ===== ALWAYS SET LIBRARY PATH FIRST =====
export LD_LIBRARY_PATH=/home/rey/unitree_g1_control/unitree_sdk2/thirdparty/lib/x86_64:$LD_LIBRARY_PATH

# ===== ROBOT STATUS =====
# Check current FSM state
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --get_fsm_id
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --get_fsm_mode

# ===== ACTIVATE ROBOT FOR MOVEMENT =====
# Set to StandUp mode (FSM ID 4) - REQUIRED BEFORE WALKING
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --set_fsm_id=4

# ===== MOVEMENT COMMANDS (Only work after FSM ID = 4) =====
# Walk forward
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --set_velocity="0.3 0 0 3"

# Walk backward
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --set_velocity="-0.2 0 0 2"

# Strafe left
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --set_velocity="0 0.2 0 2"

# Turn in place
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --set_velocity="0 0 0.5 2"

# Continuous movement (no auto-stop)
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --move="0.2 0 0"

# Stop movement
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --stop_move

# ===== SAFETY - DEACTIVATE ROBOT =====
# Return to safe state (motors passive)
./build/bin/g1_loco_client --network_interface=enx00051bd51a1a --set_fsm_id=0

# ===== LOW-LEVEL CONTROL =====
# Test ankle swing (low-level motor control)
./build/bin/g1_ankle_swing_example enx00051bd51a1a

# ===== OTHER TESTS =====
# Test audio/RPC communication
./build/bin/g1_audio_client_example enx00051bd51a1a
```

## All Available RPC Commands

| Command | Parameters | Description |
|---------|-----------|-------------|
| `--get_fsm_id` | - | Get current FSM state |
| `--get_fsm_mode` | - | Get FSM mode |
| `--set_fsm_id` | `<id>` | Set FSM state (0-4, 500) |
| `--set_velocity` | `"vx vy omega [duration]"` | Walk with velocity (auto-stops after duration) |
| `--move` | `"vx vy omega"` | Continuous movement (no auto-stop) |
| `--stop_move` | - | Stop all movement |
| `--damp` | - | Enter damping mode (FSM ID 1) |
| `--start` | - | Enter start mode (FSM ID 500) |
| `--squat` | - | Squat (FSM ID 2) |
| `--sit` | - | Sit (FSM ID 3) |
| `--stand_up` | - | Stand up (FSM ID 4) |
| `--zero_torque` | - | Zero torque mode (FSM ID 0) |
| `--balance_stand` | - | Balanced standing |
| `--low_stand` | - | Stand with low height |
| `--high_stand` | - | Stand with high height |
| `--set_stand_height` | `<height>` | Set standing height |
| `--set_swing_height` | `<height>` | Set foot swing height |
| `--set_speed_mode` | `0/1/2/3` | Set max speed (0=slowest, 3=fastest) |
| `--wave_hand` | - | Wave hand gesture |
| `--shake_hand` | - | Shake hand gesture |
