#!/usr/bin/env python3
import argparse
import bisect
import math
from typing import Dict, List, Optional, Tuple

from rclpy.serialization import deserialize_message
from rosbag2_py import ConverterOptions, SequentialReader, StorageOptions
from rosidl_runtime_py.utilities import get_message


def stamp_to_sec(stamp) -> float:
    return stamp.sec + stamp.nanosec * 1e-9


def open_reader(uri: str) -> Tuple[SequentialReader, Dict[str, str]]:
    reader = SequentialReader()
    reader.open(StorageOptions(uri=uri, storage_id="mcap"), ConverterOptions("cdr", "cdr"))
    types = {topic.name: topic.type for topic in reader.get_all_topics_and_types()}
    return reader, types


def nearest_abs_delta(times: List[float], t: float) -> Optional[float]:
    if not times:
        return None
    idx = bisect.bisect_left(times, t)
    candidates = []
    if idx < len(times):
        candidates.append(abs(times[idx] - t))
    if idx > 0:
        candidates.append(abs(times[idx - 1] - t))
    return min(candidates) if candidates else None


def summarize_bag(uri: str) -> None:
    reader, types = open_reader(uri)

    wanted = [topic for topic in ["/imu/data", "/lidar/scan", "/state_estimation"] if topic in types]
    msg_types = {topic: get_message(types[topic]) for topic in wanted}

    topic_counts = {topic: 0 for topic in wanted}
    first_stamp = {topic: None for topic in wanted}
    last_stamp = {topic: None for topic in wanted}

    imu_times: List[float] = []
    lidar_times: List[float] = []

    state_first = None
    state_last = None
    pos_min = [float("inf")] * 3
    pos_max = [float("-inf")] * 3
    vel_min = [float("inf")] * 3
    vel_max = [float("-inf")] * 3
    speed_sum = 0.0
    speed_max = 0.0

    while reader.has_next():
        topic, data, _ = reader.read_next()
        if topic not in msg_types:
            continue

        msg = deserialize_message(data, msg_types[topic])
        stamp = stamp_to_sec(msg.header.stamp)
        topic_counts[topic] += 1
        if first_stamp[topic] is None:
            first_stamp[topic] = stamp
        last_stamp[topic] = stamp

        if topic == "/imu/data":
            imu_times.append(stamp)
        elif topic == "/lidar/scan":
            lidar_times.append(stamp)
        elif topic == "/state_estimation":
            pos = (
                msg.pose.pose.position.x,
                msg.pose.pose.position.y,
                msg.pose.pose.position.z,
            )
            vel = (
                msg.twist.twist.linear.x,
                msg.twist.twist.linear.y,
                msg.twist.twist.linear.z,
            )
            speed = math.sqrt(sum(v * v for v in vel))
            if state_first is None:
                state_first = (stamp, pos, vel, speed)
            state_last = (stamp, pos, vel, speed)
            for i in range(3):
                pos_min[i] = min(pos_min[i], pos[i])
                pos_max[i] = max(pos_max[i], pos[i])
                vel_min[i] = min(vel_min[i], vel[i])
                vel_max[i] = max(vel_max[i], vel[i])
            speed_sum += speed
            speed_max = max(speed_max, speed)

    print("Bag:", uri)
    print()
    print("Topics")
    for topic in wanted:
        first = first_stamp[topic]
        last = last_stamp[topic]
        duration = (last - first) if first is not None and last is not None else 0.0
        rate = topic_counts[topic] / duration if duration > 0 else 0.0
        print(
            f"- {topic}: count={topic_counts[topic]}, "
            f"first={first}, last={last}, duration={duration:.3f}s, approx_rate={rate:.2f}Hz"
        )

    print()
    if state_first and state_last:
        p0 = state_first[1]
        p1 = state_last[1]
        drift = math.dist(p0, p1)
        pos_range = tuple(pos_max[i] - pos_min[i] for i in range(3))
        speed_avg = speed_sum / topic_counts["/state_estimation"] if topic_counts["/state_estimation"] else 0.0
        print("State Estimation")
        print(f"- first_pose={p0}")
        print(f"- last_pose={p1}")
        print(f"- endpoint_drift={drift:.3f} m")
        print(f"- position_range_xyz={pos_range}")
        print(f"- linear_velocity_min={tuple(vel_min)}")
        print(f"- linear_velocity_max={tuple(vel_max)}")
        print(f"- speed_avg={speed_avg:.3f} m/s")
        print(f"- speed_max={speed_max:.3f} m/s")

    print()
    if imu_times and lidar_times:
        lidar_to_imu = [nearest_abs_delta(imu_times, t) for t in lidar_times]
        lidar_to_imu = [d for d in lidar_to_imu if d is not None]
        if lidar_to_imu:
            lidar_to_imu.sort()
            mid = len(lidar_to_imu) // 2
            median = lidar_to_imu[mid]
            p95 = lidar_to_imu[min(len(lidar_to_imu) - 1, int(len(lidar_to_imu) * 0.95))]
            print("Timing")
            print(
                f"- nearest imu-to-lidar abs delta: "
                f"min={lidar_to_imu[0]:.6f}s, median={median:.6f}s, "
                f"p95={p95:.6f}s, max={lidar_to_imu[-1]:.6f}s"
            )
            print(
                f"- stream start delta (lidar - imu)={lidar_times[0] - imu_times[0]:.6f}s, "
                f"stream end delta (lidar - imu)={lidar_times[-1] - imu_times[-1]:.6f}s"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze static G1 SLAM bag quality.")
    parser.add_argument("bag", help="Path to rosbag2 directory")
    args = parser.parse_args()
    summarize_bag(args.bag)


if __name__ == "__main__":
    main()
