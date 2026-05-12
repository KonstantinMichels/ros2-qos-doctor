import rclpy
from rclpy.qos import DurabilityPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoPublisher, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/reliability_compatible'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
    )
    # This is compatible with best_effort_subscriber: a RELIABLE publisher can
    # satisfy a subscriber that only requests BEST_EFFORT delivery.
    node = DemoPublisher('reliable_publisher', TOPIC_NAME, qos_profile)
    spin_node(node)
