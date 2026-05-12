import rclpy
from rclpy.qos import DurabilityPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoSubscriber, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/durability_compatible'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
    )
    # This is compatible with transient_local_publisher because VOLATILE is a
    # weaker durability request than what the publisher offers.
    node = DemoSubscriber('volatile_subscriber', TOPIC_NAME, qos_profile)
    spin_node(node)
