import argparse
import sys
from typing import Optional, Sequence

import rclpy

from ros2_qos_doctor.compatibility import check_compatibility
from ros2_qos_doctor.diagnosis import TopicDiagnosis, diagnose_all_topics
from ros2_qos_doctor.endpoint_inspector import wait_for_topic_endpoints
from ros2_qos_doctor.formatting import format_system_scan, format_topic_diagnosis


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
    parser.add_argument(
        'topic_name',
        nargs='?',
        help='Topic name to inspect, for example /tf',
    )
    parser.add_argument(
        '--all',
        action='store_true',
        dest='scan_all',
        help='Scan all visible ROS 2 topics for QoS incompatibilities.',
    )
    parser.add_argument(
        '--show-compatible',
        action='store_true',
        help='With --all, also print topics without detected QoS incompatibilities.',
    )
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


def validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if bool(args.topic_name) == args.scan_all:
        parser.error('provide exactly one of a topic name or --all')
    if args.show_compatible and not args.scan_all:
        parser.error('--show-compatible can only be used with --all')


def run(
    topic_name: Optional[str] = None,
    include_rosbag2_yaml: bool = False,
    timeout_sec: float = 2.0,
    scan_all: bool = False,
    show_compatible: bool = False,
) -> int:
    rclpy.init(args=None)
    node = None
    try:
        node = rclpy.create_node('_ros2_qos_doctor_inspector')
        if scan_all:
            scan_result = diagnose_all_topics(node, discovery_timeout_sec=timeout_sec)
            print(
                format_system_scan(
                    scan_result,
                    show_compatible=show_compatible,
                    include_rosbag2_yaml=include_rosbag2_yaml,
                )
            )
            return 0

        if topic_name is None:
            raise ValueError('topic_name is required unless scan_all is true')

        publishers, subscribers = wait_for_topic_endpoints(
            node,
            topic_name,
            timeout_sec=timeout_sec,
        )
        report = check_compatibility(publishers, subscribers)
        print(
            format_topic_diagnosis(
                TopicDiagnosis(
                    topic_name=topic_name,
                    topic_types=[],
                    publishers=publishers,
                    subscribers=subscribers,
                    compatibility=report,
                ),
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
    validate_args(parser, args)
    return run(
        args.topic_name,
        include_rosbag2_yaml=args.rosbag2_yaml,
        timeout_sec=args.timeout,
        scan_all=args.scan_all,
        show_compatible=args.show_compatible,
    )


if __name__ == '__main__':
    sys.exit(main())
