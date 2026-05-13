import rclpy
from rclpy.duration import Duration
from rclpy.qos import DurabilityPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoPublisher, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/deadline'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
        deadline=Duration(seconds=2),
    )
    # This intentionally mismatches deadline_mismatch_subscriber: the publisher
    # offers a slower maximum interval than the subscriber requests.
    node = DemoPublisher('deadline_mismatch_publisher', TOPIC_NAME, qos_profile)
    spin_node(node)
