import rclpy
from rclpy.qos import DurabilityPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoPublisher, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/durability'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
    )
    # This intentionally mismatches transient_local_subscriber: a VOLATILE
    # publisher cannot satisfy a subscriber that requests TRANSIENT_LOCAL data.
    node = DemoPublisher('volatile_publisher', TOPIC_NAME, qos_profile)
    spin_node(node)
