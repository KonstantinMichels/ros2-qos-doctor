import rclpy
from rclpy.duration import Duration
from rclpy.qos import DurabilityPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoSubscriber, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/lease_duration_compatible'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
        liveliness_lease_duration=Duration(seconds=2),
    )
    # This is compatible with lease_compatible_publisher because the subscriber
    # accepts liveliness leases up to 2 seconds.
    node = DemoSubscriber('lease_compatible_subscriber', TOPIC_NAME, qos_profile)
    spin_node(node)
