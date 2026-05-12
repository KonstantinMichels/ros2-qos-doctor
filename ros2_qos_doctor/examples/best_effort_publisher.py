import rclpy
from rclpy.qos import DurabilityPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoPublisher, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/reliability'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.BEST_EFFORT,
        durability=DurabilityPolicy.VOLATILE,
    )
    # This intentionally mismatches reliable_subscriber: a BEST_EFFORT publisher
    # cannot satisfy a subscriber that requests RELIABLE delivery.
    node = DemoPublisher('best_effort_publisher', TOPIC_NAME, qos_profile)
    spin_node(node)
