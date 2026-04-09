#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
START_RVIZ="${ENABLE_RVIZ:-auto}"
LAUNCH_ARGS=()
G1_WS="/home/mhw/unitree_project/g1_ros_package"
LAUNCH_PID=""
RVIZ_PID=""
_CLEANED_UP=0

cleanup() {
  if [[ "${_CLEANED_UP}" -eq 1 ]]; then
    return
  fi
  _CLEANED_UP=1

  if [[ -n "${RVIZ_PID}" ]] && kill -0 "${RVIZ_PID}" 2>/dev/null; then
    kill -INT "${RVIZ_PID}" 2>/dev/null || true
    wait "${RVIZ_PID}" 2>/dev/null || true
  fi

  if [[ -n "${LAUNCH_PID}" ]] && kill -0 "${LAUNCH_PID}" 2>/dev/null; then
    kill -INT "${LAUNCH_PID}" 2>/dev/null || true
    wait "${LAUNCH_PID}" 2>/dev/null || true
  fi
}

trap cleanup INT TERM EXIT

for arg in "$@"; do
  case "$arg" in
    --no-rviz)
      START_RVIZ=0
      ;;
    --rviz)
      START_RVIZ=1
      ;;
    *)
      LAUNCH_ARGS+=("$arg")
      ;;
  esac
done

cd "$SCRIPT_DIR"
source ./install/setup.bash

if [[ -f "${G1_WS}/install/setup.bash" ]]; then
  source "${G1_WS}/install/setup.bash"
else
  echo "Missing ${G1_WS}/install/setup.bash. Build g1_controller first."
  exit 1
fi

if [[ "$START_RVIZ" == "auto" ]]; then
  if [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]]; then
    START_RVIZ=1
  else
    START_RVIZ=0
  fi
fi

ROS_DOMAIN_ID=1 ros2 launch vehicle_simulator system_real_robot_g1_bridge.launch.py "${LAUNCH_ARGS[@]}" &
LAUNCH_PID=$!

if [[ "$START_RVIZ" == "1" ]]; then
  sleep 1
  ROS_DOMAIN_ID=1 ros2 run rviz2 rviz2 -d src/base_autonomy/vehicle_simulator/rviz/vehicle_simulator.rviz &
  RVIZ_PID=$!
  wait "${RVIZ_PID}"
else
  echo "Skipping RViz launch. Run RViz from a remote workstation or pass --rviz to force it."
  wait "${LAUNCH_PID}"
fi
