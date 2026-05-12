import rclpy
from rclpy.qos import DurabilityPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoPublisher, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/durability_compatible'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.TRANSIENT_LOCAL,
    )
    # This is compatible with volatile_subscriber because TRANSIENT_LOCAL offers
    # at least as much durability as a VOLATILE subscriber requests.
    node = DemoPublisher('transient_local_publisher', TOPIC_NAME, qos_profile)
    spin_node(node)
