import rclpy
from rclpy.qos import DurabilityPolicy, LivelinessPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoPublisher, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/liveliness_compatible'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
        liveliness=LivelinessPolicy.MANUAL_BY_TOPIC,
    )
    # This is compatible with liveliness_compatible_subscriber because
    # MANUAL_BY_TOPIC offers at least as much liveliness control as AUTOMATIC.
    node = DemoPublisher(
        'liveliness_compatible_publisher',
        TOPIC_NAME,
        qos_profile,
        assert_liveliness=True,
    )
    spin_node(node)
