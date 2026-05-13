import rclpy
from rclpy.qos import DurabilityPolicy, LivelinessPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoPublisher, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/liveliness'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
        liveliness=LivelinessPolicy.AUTOMATIC,
    )
    # This intentionally mismatches liveliness_mismatch_subscriber: AUTOMATIC
    # liveliness cannot satisfy a MANUAL_BY_TOPIC subscriber request.
    node = DemoPublisher('liveliness_mismatch_publisher', TOPIC_NAME, qos_profile)
    spin_node(node)
