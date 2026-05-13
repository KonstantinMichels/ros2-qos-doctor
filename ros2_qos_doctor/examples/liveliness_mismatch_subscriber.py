import rclpy
from rclpy.qos import DurabilityPolicy, LivelinessPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoSubscriber, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/liveliness'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
        liveliness=LivelinessPolicy.MANUAL_BY_TOPIC,
    )
    # This subscriber requests MANUAL_BY_TOPIC liveliness, which is stronger
    # than the AUTOMATIC liveliness offered by the mismatch publisher.
    node = DemoSubscriber('liveliness_mismatch_subscriber', TOPIC_NAME, qos_profile)
    spin_node(node)
