import rclpy
from rclpy.duration import Duration
from rclpy.qos import DurabilityPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoPublisher, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/lease_duration'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
        liveliness_lease_duration=Duration(seconds=2),
    )
    # This intentionally mismatches lease_mismatch_subscriber: the publisher
    # offers a longer liveliness lease duration than the subscriber requests.
    node = DemoPublisher('lease_mismatch_publisher', TOPIC_NAME, qos_profile)
    spin_node(node)
