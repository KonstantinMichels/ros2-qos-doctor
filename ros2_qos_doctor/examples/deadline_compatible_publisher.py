import rclpy
from rclpy.duration import Duration
from rclpy.qos import DurabilityPolicy, ReliabilityPolicy

from ros2_qos_doctor.examples.common import DemoPublisher, make_qos_profile, spin_node


TOPIC_NAME = '/qos_demo/deadline_compatible'


def main(args=None) -> None:
    rclpy.init(args=args)
    qos_profile = make_qos_profile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
        deadline=Duration(seconds=1),
    )
    # This is compatible with deadline_compatible_subscriber because the
    # publisher offers a deadline no slower than the subscriber requests.
    node = DemoPublisher('deadline_compatible_publisher', TOPIC_NAME, qos_profile)
    spin_node(node)
