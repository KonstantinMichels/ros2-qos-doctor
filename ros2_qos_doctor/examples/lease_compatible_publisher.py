import rclpy
from rclpy.duration import Duration
from rclpy.qos import DurabilityPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoPublisher, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/lease_duration_compatible'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
        liveliness_lease_duration=Duration(seconds=1),
    )
    # This is compatible with lease_compatible_subscriber because the publisher
    # offers a lease duration no longer than the subscriber requests.
    node = DemoPublisher('lease_compatible_publisher', TOPIC_NAME, qos_profile)
    spin_node(node)
