import rclpy
from rclpy.duration import Duration
from rclpy.qos import DurabilityPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoSubscriber, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/deadline_compatible'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
        deadline=Duration(seconds=2),
    )
    # This is compatible with deadline_compatible_publisher because the
    # subscriber accepts intervals up to 2 seconds.
    node = DemoSubscriber('deadline_compatible_subscriber', TOPIC_NAME, qos_profile)
    spin_node(node)
