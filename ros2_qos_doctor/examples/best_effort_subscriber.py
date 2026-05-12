import rclpy
from rclpy.qos import DurabilityPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoSubscriber, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/reliability_compatible'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.BEST_EFFORT,
        durability=DurabilityPolicy.VOLATILE,
    )
    # This is compatible with reliable_publisher because BEST_EFFORT is a weaker
    # request than what the publisher offers.
    node = DemoSubscriber('best_effort_subscriber', TOPIC_NAME, qos_profile)
    spin_node(node)
