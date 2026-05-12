import argparse
import sys
from typing import Optional, Sequence

import rclpy

from ros2_qos_doctor.compatibility import check_compatibility
from ros2_qos_doctor.endpoint_inspector import wait_for_topic_endpoints
from ros2_qos_doctor.formatting import format_report


def non_negative_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0.0:
        raise argparse.ArgumentTypeError('must be greater than or equal to 0')
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='qos_doctor',
        description='Diagnose ROS 2 QoS compatibility for a topic.',
    )
    parser.add_argument('topic_name', help='Topic name to inspect, for example /tf')
    parser.add_argument(
        '--rosbag2-yaml',
        action='store_true',
        help='Print a suggested rosbag2 QoS override YAML snippet when possible.',
    )
    parser.add_argument(
        '--timeout',
        type=non_negative_float,
        default=2.0,
        help='Seconds to wait for ROS graph discovery before reporting results.',
    )
    return parser


def run(
    topic_name: str,
    include_rosbag2_yaml: bool = False,
    timeout_sec: float = 2.0,
) -> int:
    rclpy.init(args=None)
    node = None
    try:
        node = rclpy.create_node('_ros2_qos_doctor_inspector')
        publishers, subscribers = wait_for_topic_endpoints(
            node,
            topic_name,
            timeout_sec=timeout_sec,
        )
        report = check_compatibility(publishers, subscribers)
        print(
            format_report(
                topic_name,
                publishers,
                subscribers,
                report,
                include_rosbag2_yaml=include_rosbag2_yaml,
            )
        )
        return 0
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(
        args.topic_name,
        include_rosbag2_yaml=args.rosbag2_yaml,
        timeout_sec=args.timeout,
    )


if __name__ == '__main__':
    sys.exit(main())
