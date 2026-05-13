from dataclasses import dataclass
from typing import Iterable, List, Optional

import rclpy

from ros2_qos_doctor.compatibility import CompatibilityReport, EndpointQoS, check_compatibility
from ros2_qos_doctor.endpoint_inspector import inspect_topic, topic_names_with_types


@dataclass(frozen=True)
class TopicDiagnosis:
    topic_name: str
    topic_types: List[str]
    publishers: List[EndpointQoS]
    subscribers: List[EndpointQoS]
    compatibility: CompatibilityReport

    @property
    def has_publishers_and_subscribers(self) -> bool:
        return bool(self.publishers and self.subscribers)

    @property
    def has_issues(self) -> bool:
        return bool(self.compatibility.issues)


@dataclass(frozen=True)
class SystemScanResult:
    scanned_topic_count: int
    topics_with_publishers_and_subscribers_count: int
    topics_with_issues_count: int
    diagnoses: List[TopicDiagnosis]


def _endpoint_belongs_to_node(
    endpoint: EndpointQoS,
    node_name: str,
    node_namespace: str,
) -> bool:
    return endpoint.node_name == node_name and endpoint.node_namespace == node_namespace


def _remove_self_endpoints(
    endpoints: Iterable[EndpointQoS],
    node: object,
) -> List[EndpointQoS]:
    node_name = node.get_name()
    node_namespace = node.get_namespace()
    return [
        endpoint for endpoint in endpoints
        if not _endpoint_belongs_to_node(endpoint, node_name, node_namespace)
    ]


def diagnose_topic(
    topic_name: str,
    node: object,
    topic_types: Optional[List[str]] = None,
) -> TopicDiagnosis:
    publishers, subscribers = inspect_topic(node, topic_name)
    publishers = _remove_self_endpoints(publishers, node)
    subscribers = _remove_self_endpoints(subscribers, node)
    compatibility = check_compatibility(publishers, subscribers)
    return TopicDiagnosis(
        topic_name=topic_name,
        topic_types=topic_types or [],
        publishers=publishers,
        subscribers=subscribers,
        compatibility=compatibility,
    )


def build_system_scan_result(diagnoses: Iterable[TopicDiagnosis]) -> SystemScanResult:
    diagnosis_list = list(diagnoses)
    return SystemScanResult(
        scanned_topic_count=len(diagnosis_list),
        topics_with_publishers_and_subscribers_count=sum(
            diagnosis.has_publishers_and_subscribers
            for diagnosis in diagnosis_list
        ),
        topics_with_issues_count=sum(
            diagnosis.has_issues
            for diagnosis in diagnosis_list
        ),
        diagnoses=diagnosis_list,
    )


def diagnose_all_topics(
    node: object,
    discovery_timeout_sec: float = 2.0,
) -> SystemScanResult:
    rclpy.spin_once(node, timeout_sec=discovery_timeout_sec)
    diagnoses = [
        diagnose_topic(topic_name, node, topic_types=list(types))
        for topic_name, types in topic_names_with_types(node)
    ]
    return build_system_scan_result(diagnoses)
