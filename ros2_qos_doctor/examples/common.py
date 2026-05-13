import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    LivelinessPolicy,
    QoSProfile,
    ReliabilityPolicy,
)
from std_msgs.msg import String


def make_qos_profile(
    reliability: ReliabilityPolicy,
    durability: DurabilityPolicy,
    deadline: Duration | None = None,
    liveliness: LivelinessPolicy = LivelinessPolicy.AUTOMATIC,
    liveliness_lease_duration: Duration | None = None,
) -> QoSProfile:
    return QoSProfile(
        reliability=reliability,
        durability=durability,
        history=HistoryPolicy.KEEP_LAST,
        depth=10,
        deadline=deadline or Duration(),
        liveliness=liveliness,
        liveliness_lease_duration=liveliness_lease_duration or Duration(),
    )


def duration_summary(duration: Duration) -> str:
    if duration.nanoseconds == 0:
        return 'DEFAULT'
    return f'{duration.nanoseconds} ns'


def qos_summary(qos_profile: QoSProfile) -> str:
    return (
        f'reliability={qos_profile.reliability.name}, '
        f'durability={qos_profile.durability.name}, '
        f'history={qos_profile.history.name}, '
        f'depth={qos_profile.depth}, '
        f'deadline={duration_summary(qos_profile.deadline)}, '
        f'liveliness={qos_profile.liveliness.name}, '
        'liveliness_lease_duration='
        f'{duration_summary(qos_profile.liveliness_lease_duration)}'
    )


class DemoPublisher(Node):
    def __init__(
        self,
        node_name: str,
        topic_name: str,
        qos_profile: QoSProfile,
        assert_liveliness: bool = False,
    ):
        super().__init__(node_name)
        self._count = 0
        self._topic_name = topic_name
        self._publisher = self.create_publisher(String, topic_name, qos_profile)
        self._assert_liveliness = assert_liveliness
        self._timer = self.create_timer(1.0, self._publish)
        self.get_logger().info(f'Publishing on {topic_name}')
        self.get_logger().info(f'QoS: {qos_summary(qos_profile)}')

    def _publish(self) -> None:
        message = String()
        message.data = f'{self.get_name()} message {self._count}'
        self._publisher.publish(message)
        if self._assert_liveliness:
            try:
                self._publisher.assert_liveliness()
            except AttributeError:
                self.get_logger().warn('Manual liveliness assertion is not available.')
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
