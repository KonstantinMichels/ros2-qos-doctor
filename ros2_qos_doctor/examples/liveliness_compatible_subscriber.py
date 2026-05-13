import rclpy
from rclpy.qos import DurabilityPolicy, LivelinessPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoSubscriber, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/liveliness_compatible'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
        liveliness=LivelinessPolicy.AUTOMATIC,
    )
    # This is compatible with liveliness_compatible_publisher because AUTOMATIC
    # is a weaker liveliness request than MANUAL_BY_TOPIC offers.
    node = DemoSubscriber('liveliness_compatible_subscriber', TOPIC_NAME, qos_profile)
    spin_node(node)
