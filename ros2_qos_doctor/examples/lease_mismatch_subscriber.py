import rclpy
from rclpy.duration import Duration
from rclpy.qos import DurabilityPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoSubscriber, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/lease_duration'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
        liveliness_lease_duration=Duration(seconds=1),
    )
    # This subscriber requests a 1 second liveliness lease, but the publisher
    # only offers 2 seconds, so the QoS profiles are incompatible.
    node = DemoSubscriber('lease_mismatch_subscriber', TOPIC_NAME, qos_profile)
    spin_node(node)
