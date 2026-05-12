import rclpy
from rclpy.qos import DurabilityPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoSubscriber, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/durability'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.TRANSIENT_LOCAL,
    )
    # This subscriber requests TRANSIENT_LOCAL durability, so it is incompatible
    # with the VOLATILE publisher in the durability mismatch demo.
    node = DemoSubscriber('transient_local_subscriber', TOPIC_NAME, qos_profile)
    spin_node(node)
