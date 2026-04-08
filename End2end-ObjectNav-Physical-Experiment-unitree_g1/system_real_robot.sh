#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
START_RVIZ="${ENABLE_RVIZ:-auto}"
LAUNCH_ARGS=()

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

cd $SCRIPT_DIR
source ./install/setup.bash

if [[ "$START_RVIZ" == "auto" ]]; then
  if [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]]; then
    START_RVIZ=1
  else
    START_RVIZ=0
  fi
fi

ROS_DOMAIN_ID=1 ros2 launch vehicle_simulator system_real_robot.launch "${LAUNCH_ARGS[@]}" &

if [[ "$START_RVIZ" == "1" ]]; then
  sleep 1
  ROS_DOMAIN_ID=1 ros2 run rviz2 rviz2 -d src/base_autonomy/vehicle_simulator/rviz/vehicle_simulator.rviz
else
  echo "Skipping RViz launch. Run RViz from a remote workstation or pass --rviz to force it."
  wait
fi
