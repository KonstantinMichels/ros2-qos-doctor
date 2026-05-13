from dataclasses import dataclass

from rclpy.duration import Duration
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    LivelinessPolicy,
    QoSProfile,
    ReliabilityPolicy,
)

from ros2_qos_doctor.compatibility import EndpointKind
from ros2_qos_doctor.endpoint_inspector import (
    endpoint_info_to_qos,
    inspect_topic,
    wait_for_topic_endpoints,
)


@dataclass
class FakeEndpointInfo:
    node_name: str
    node_namespace: str
    topic_type: str
    qos_profile: object


@dataclass
class FakeQoSProfile:
    reliability: object = 'UNKNOWN'
    durability: object = 'UNKNOWN'
    history: object = 'UNKNOWN'
    depth: int = 0
    liveliness: object = 'UNKNOWN'


def test_endpoint_info_to_qos_reads_jazzy_endpoint_fields_without_ros_graph():
    endpoint_info = FakeEndpointInfo(
        node_name='camera',
        node_namespace='/robot',
        topic_type='sensor_msgs/msg/Image',
        qos_profile=QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=5,
            deadline=Duration(seconds=2),
            lifespan=Duration(seconds=3),
            liveliness=LivelinessPolicy.AUTOMATIC,
            liveliness_lease_duration=Duration(seconds=4),
        ),
    )

    qos = endpoint_info_to_qos(endpoint_info, EndpointKind.PUBLISHER)

    assert qos.node_name == 'camera'
    assert qos.node_namespace == '/robot'
    assert qos.topic_type == 'sensor_msgs/msg/Image'
    assert qos.reliability == 'best_effort'
    assert qos.durability == 'volatile'
    assert qos.history == 'keep_last'
    assert qos.depth == 5
    assert qos.deadline == 2_000_000_000
    assert qos.lifespan == 3_000_000_000
    assert qos.liveliness == 'automatic'
    assert qos.liveliness_lease_duration == 4_000_000_000


class FakeNode:
    def __init__(
        self,
        publisher_sequences,
        subscriber_sequences,
        graph_nodes=None,
        publisher_topics_by_node=None,
        subscriber_topics_by_node=None,
    ):
        self.publisher_sequences = list(publisher_sequences)
        self.subscriber_sequences = list(subscriber_sequences)
        self.graph_nodes = graph_nodes or []
        self.publisher_topics_by_node = publisher_topics_by_node or {}
        self.subscriber_topics_by_node = subscriber_topics_by_node or {}
        self.calls = 0

    def get_publishers_info_by_topic(self, topic_name):
        index = min(self.calls, len(self.publisher_sequences) - 1)
        return self.publisher_sequences[index]

    def get_subscriptions_info_by_topic(self, topic_name):
        index = min(self.calls, len(self.subscriber_sequences) - 1)
        self.calls += 1
        return self.subscriber_sequences[index]

    def get_node_names_and_namespaces(self):
        return self.graph_nodes

    def get_publisher_names_and_types_by_node(self, node_name, namespace):
        return self.publisher_topics_by_node.get((node_name, namespace), [])

    def get_subscriber_names_and_types_by_node(self, node_name, namespace):
        return self.subscriber_topics_by_node.get((node_name, namespace), [])


def test_wait_for_topic_endpoints_retries_while_graph_discovery_catches_up(monkeypatch):
    endpoint_info = FakeEndpointInfo(
        node_name='talker',
        node_namespace='/',
        topic_type='std_msgs/msg/String',
        qos_profile=QoSProfile(depth=10),
    )
    node = FakeNode(
        publisher_sequences=[[], [endpoint_info]],
        subscriber_sequences=[[], []],
    )
    spin_calls = []
    monkeypatch.setattr(
        'ros2_qos_doctor.endpoint_inspector.rclpy.spin_once',
        lambda node, timeout_sec: spin_calls.append(timeout_sec),
    )

    publishers, subscribers = wait_for_topic_endpoints(node, '/chatter', timeout_sec=0.2)

    assert len(publishers) == 1
    assert subscribers == []
    assert spin_calls


def test_wait_for_topic_endpoints_keeps_waiting_after_first_endpoint(monkeypatch):
    publisher_info = FakeEndpointInfo(
        node_name='talker',
        node_namespace='/',
        topic_type='std_msgs/msg/String',
        qos_profile=QoSProfile(depth=10),
    )
    subscriber_info = FakeEndpointInfo(
        node_name='listener',
        node_namespace='/',
        topic_type='std_msgs/msg/String',
        qos_profile=QoSProfile(depth=10),
    )
    node = FakeNode(
        publisher_sequences=[[publisher_info], [publisher_info]],
        subscriber_sequences=[[], [subscriber_info]],
    )

    def spin_once(node, timeout_sec):
        return None

    monkeypatch.setattr('ros2_qos_doctor.endpoint_inspector.rclpy.spin_once', spin_once)

    publishers, subscribers = wait_for_topic_endpoints(node, '/chatter', timeout_sec=0.2)

    assert len(publishers) == 1
    assert len(subscribers) == 1


def test_wait_for_topic_endpoints_keeps_best_snapshot_when_final_read_is_partial(monkeypatch):
    publisher_info = FakeEndpointInfo(
        node_name='talker',
        node_namespace='/',
        topic_type='std_msgs/msg/String',
        qos_profile=QoSProfile(depth=10),
    )
    subscriber_info = FakeEndpointInfo(
        node_name='listener',
        node_namespace='/',
        topic_type='std_msgs/msg/String',
        qos_profile=QoSProfile(depth=10),
    )
    node = FakeNode(
        publisher_sequences=[[publisher_info], [publisher_info], [publisher_info]],
        subscriber_sequences=[[subscriber_info], [], []],
    )

    monkeypatch.setattr(
        'ros2_qos_doctor.endpoint_inspector.rclpy.spin_once',
        lambda node, timeout_sec: None,
    )

    publishers, subscribers = wait_for_topic_endpoints(node, '/chatter', timeout_sec=0.2)

    assert len(publishers) == 1
    assert len(subscribers) == 1


def test_inspect_topic_resolves_unknown_endpoint_node_names_from_graph():
    publisher_info = FakeEndpointInfo(
        node_name='_NODE_NAME_UNKNOWN_',
        node_namespace='_NODE_NAMESPACE_UNKNOWN_',
        topic_type='std_msgs/msg/String',
        qos_profile=QoSProfile(depth=10),
    )
    subscriber_info = FakeEndpointInfo(
        node_name='_NODE_NAME_UNKNOWN_',
        node_namespace='_NODE_NAMESPACE_UNKNOWN_',
        topic_type='std_msgs/msg/String',
        qos_profile=QoSProfile(depth=10),
    )
    node = FakeNode(
        publisher_sequences=[[publisher_info]],
        subscriber_sequences=[[subscriber_info]],
        graph_nodes=[('talker', ''), ('listener', '')],
        publisher_topics_by_node={
            ('talker', ''): [('chatter', ['std_msgs/msg/String'])],
        },
        subscriber_topics_by_node={
            ('listener', ''): [('chatter', ['std_msgs/msg/String'])],
        },
    )

    publishers, subscribers = inspect_topic(node, '/chatter')

    assert publishers[0].full_node_name == '/talker'
    assert subscribers[0].full_node_name == '/listener'


def test_inspect_topic_leaves_unknown_names_when_graph_resolution_is_ambiguous():
    endpoint_info = FakeEndpointInfo(
        node_name='_NODE_NAME_UNKNOWN_',
        node_namespace='_NODE_NAMESPACE_UNKNOWN_',
        topic_type='std_msgs/msg/String',
        qos_profile=QoSProfile(depth=10),
    )
    node = FakeNode(
        publisher_sequences=[[endpoint_info]],
        subscriber_sequences=[[]],
        graph_nodes=[('talker_a', ''), ('talker_b', '')],
        publisher_topics_by_node={
            ('talker_a', ''): [('chatter', ['std_msgs/msg/String'])],
            ('talker_b', ''): [('chatter', ['std_msgs/msg/String'])],
        },
    )

    publishers, subscribers = inspect_topic(node, '/chatter')

    assert subscribers == []
    assert publishers[0].node_name == '_NODE_NAME_UNKNOWN_'


def test_unknown_history_with_zero_depth_is_reported_as_unknown_depth():
    endpoint_info = FakeEndpointInfo(
        node_name='talker',
        node_namespace='/',
        topic_type='std_msgs/msg/String',
        qos_profile=FakeQoSProfile(),
    )

    qos = endpoint_info_to_qos(endpoint_info, EndpointKind.PUBLISHER)

    assert qos.history == 'unknown'
    assert qos.depth is None
