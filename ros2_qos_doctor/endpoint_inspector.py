from dataclasses import replace
import time
from typing import Iterable, List, Sequence

import rclpy

from ros2_qos_doctor.compatibility import (
    EndpointKind,
    EndpointQoS,
    duration_to_nanoseconds,
    normalize_policy,
)


UNKNOWN_POLICY = 'unknown'
UNKNOWN_NODE_NAME = '_NODE_NAME_UNKNOWN_'
UNKNOWN_NODE_NAMESPACE = '_NODE_NAMESPACE_UNKNOWN_'
SPIN_INTERVAL_SEC = 0.1


def _field_value(profile: object, field_name: str, default=None):
    return getattr(profile, field_name, default)


def _normalize_depth(history: str, depth: object):
    if history == UNKNOWN_POLICY and depth == 0:
        return None
    return depth


def endpoint_info_to_qos(endpoint_info: object, endpoint_kind: EndpointKind) -> EndpointQoS:
    profile = endpoint_info.qos_profile
    history = normalize_policy(_field_value(profile, 'history'))
    depth = _field_value(profile, 'depth')
    liveliness = normalize_policy(_field_value(profile, 'liveliness'))
    return EndpointQoS(
        node_name=endpoint_info.node_name,
        node_namespace=endpoint_info.node_namespace,
        topic_type=getattr(endpoint_info, 'topic_type', None),
        reliability=normalize_policy(_field_value(profile, 'reliability')),
        durability=normalize_policy(_field_value(profile, 'durability')),
        history=history,
        depth=_normalize_depth(history, depth),
        deadline=duration_to_nanoseconds(_field_value(profile, 'deadline')),
        lifespan=duration_to_nanoseconds(_field_value(profile, 'lifespan')),
        liveliness=None if liveliness == UNKNOWN_POLICY else liveliness,
        liveliness_lease_duration=duration_to_nanoseconds(
            _field_value(profile, 'liveliness_lease_duration')
        ),
        endpoint_kind=endpoint_kind,
    )


def _publisher_endpoint_qos(node: object, topic_name: str) -> List[EndpointQoS]:
    return [
        endpoint_info_to_qos(info, EndpointKind.PUBLISHER)
        for info in node.get_publishers_info_by_topic(topic_name)
    ]


def _subscriber_endpoint_qos(node: object, topic_name: str) -> List[EndpointQoS]:
    return [
        endpoint_info_to_qos(info, EndpointKind.SUBSCRIBER)
        for info in node.get_subscriptions_info_by_topic(topic_name)
    ]


def inspect_topic(node: object, topic_name: str) -> tuple[List[EndpointQoS], List[EndpointQoS]]:
    publishers = _publisher_endpoint_qos(node, topic_name)
    subscribers = _subscriber_endpoint_qos(node, topic_name)
    return (
        resolve_unknown_node_names(node, topic_name, publishers, EndpointKind.PUBLISHER),
        resolve_unknown_node_names(node, topic_name, subscribers, EndpointKind.SUBSCRIBER),
    )


def _is_unknown_node(endpoint: EndpointQoS) -> bool:
    return endpoint.node_name in ('', UNKNOWN_NODE_NAME)


def _normalize_namespace(namespace: str) -> str:
    if not namespace or namespace == UNKNOWN_NODE_NAMESPACE:
        return '/'
    return namespace


def _topic_is_listed(topic_name: str, names_and_types: Iterable[tuple[str, list[str]]]) -> bool:
    return any(
        name == topic_name or name.lstrip('/') == topic_name.lstrip('/')
        for name, _types in names_and_types
    )


def _nodes_for_topic(
    node: object,
    topic_name: str,
    endpoint_kind: EndpointKind,
) -> List[tuple[str, str]]:
    nodes: List[tuple[str, str]] = []
    graph_method_name = (
        'get_publisher_names_and_types_by_node'
        if endpoint_kind == EndpointKind.PUBLISHER
        else 'get_subscriber_names_and_types_by_node'
    )
    graph_method = getattr(node, graph_method_name)

    for node_name, raw_namespace in node.get_node_names_and_namespaces():
        try:
            names_and_types = graph_method(node_name, raw_namespace)
        except RuntimeError:
            continue
        if _topic_is_listed(topic_name, names_and_types):
            nodes.append((node_name, _normalize_namespace(raw_namespace)))

    return nodes


def resolve_unknown_node_names(
    node: object,
    topic_name: str,
    endpoints: Sequence[EndpointQoS],
    endpoint_kind: EndpointKind,
) -> List[EndpointQoS]:
    unknown_indexes = [
        index for index, endpoint in enumerate(endpoints)
        if _is_unknown_node(endpoint)
    ]
    if not unknown_indexes:
        return list(endpoints)

    candidates = _nodes_for_topic(node, topic_name, endpoint_kind)
    if len(candidates) != len(unknown_indexes):
        return list(endpoints)

    resolved = list(endpoints)
    for index, (node_name, namespace) in zip(unknown_indexes, candidates):
        resolved[index] = replace(
            resolved[index],
            node_name=node_name,
            node_namespace=namespace,
        )
    return resolved


def _snapshot_score(
    publishers: Sequence[EndpointQoS],
    subscribers: Sequence[EndpointQoS],
) -> tuple[int, int, int]:
    known_nodes = sum(
        not _is_unknown_node(endpoint)
        for endpoint in [*publishers, *subscribers]
    )
    has_both_kinds = int(bool(publishers and subscribers))
    return (has_both_kinds, len(publishers) + len(subscribers), known_nodes)


def _better_snapshot(
    current: tuple[List[EndpointQoS], List[EndpointQoS]],
    candidate: tuple[List[EndpointQoS], List[EndpointQoS]],
) -> tuple[List[EndpointQoS], List[EndpointQoS]]:
    if _snapshot_score(*candidate) >= _snapshot_score(*current):
        return candidate
    return current


def wait_for_topic_endpoints(
    node: object,
    topic_name: str,
    timeout_sec: float = 2.0,
) -> tuple[List[EndpointQoS], List[EndpointQoS]]:
    deadline = time.monotonic() + timeout_sec
    best_snapshot: tuple[List[EndpointQoS], List[EndpointQoS]] = ([], [])

    while time.monotonic() < deadline:
        snapshot = inspect_topic(node, topic_name)
        if snapshot[0] or snapshot[1]:
            best_snapshot = _better_snapshot(best_snapshot, snapshot)

        rclpy.spin_once(node, timeout_sec=SPIN_INTERVAL_SEC)

    snapshot = inspect_topic(node, topic_name)
    if snapshot[0] or snapshot[1]:
        best_snapshot = _better_snapshot(best_snapshot, snapshot)

    return best_snapshot


def topic_names_with_types(node: object) -> Iterable[tuple[str, List[str]]]:
    return node.get_topic_names_and_types()
