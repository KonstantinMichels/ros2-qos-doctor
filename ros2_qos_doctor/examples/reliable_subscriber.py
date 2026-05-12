import rclpy
from rclpy.qos import DurabilityPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoSubscriber, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/reliability'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
    )
    # This subscriber requests RELIABLE delivery, so it is incompatible with the
    # BEST_EFFORT publisher in the reliability mismatch demo.
    node = DemoSubscriber('reliable_subscriber', TOPIC_NAME, qos_profile)
    spin_node(node)
