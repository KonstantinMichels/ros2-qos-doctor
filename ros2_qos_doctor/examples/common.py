import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String


def make_qos_profile(
    reliability: ReliabilityPolicy,
    durability: DurabilityPolicy,
) -> QoSProfile:
    return QoSProfile(
        reliability=reliability,
        durability=durability,
        history=HistoryPolicy.KEEP_LAST,
        depth=10,
    )


def qos_summary(qos_profile: QoSProfile) -> str:
    return (
        f'reliability={qos_profile.reliability.name}, '
        f'durability={qos_profile.durability.name}, '
        f'history={qos_profile.history.name}, '
        f'depth={qos_profile.depth}'
    )


class DemoPublisher(Node):
    def __init__(self, node_name: str, topic_name: str, qos_profile: QoSProfile):
        super().__init__(node_name)
        self._count = 0
        self._topic_name = topic_name
        self._publisher = self.create_publisher(String, topic_name, qos_profile)
        self._timer = self.create_timer(1.0, self._publish)
        self.get_logger().info(f'Publishing on {topic_name}')
        self.get_logger().info(f'QoS: {qos_summary(qos_profile)}')

    def _publish(self) -> None:
        message = String()
        message.data = f'{self.get_name()} message {self._count}'
        self._publisher.publish(message)
        self.get_logger().info(f'Published on {self._topic_name}: "{message.data}"')
        self._count += 1


class DemoSubscriber(Node):
    def __init__(self, node_name: str, topic_name: str, qos_profile: QoSProfile):
        super().__init__(node_name)
        self._topic_name = topic_name
        self._subscription = self.create_subscription(
            String,
            topic_name,
            self._on_message,
            qos_profile,
        )
        self.get_logger().info(f'Subscribing to {topic_name}')
        self.get_logger().info(f'QoS: {qos_summary(qos_profile)}')

    def _on_message(self, message: String) -> None:
        self.get_logger().info(f'Received on {self._topic_name}: "{message.data}"')


def spin_node(node: Node) -> None:
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
