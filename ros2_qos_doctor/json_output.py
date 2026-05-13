import json
from typing import Any, Optional

from ros2_qos_doctor.compatibility import CompatibilityIssue, EndpointQoS
from ros2_qos_doctor.diagnosis import SystemScanResult, TopicDiagnosis


def _none_if_unknown(value: Any) -> Any:
    if value in ('unknown', 'system_default', None):
        return None
    return value


def endpoint_to_dict(endpoint: EndpointQoS) -> dict:
    return {
        'node_name': endpoint.node_name,
        'node_namespace': endpoint.node_namespace,
        'full_node_name': endpoint.full_node_name,
        'topic_type': endpoint.topic_type,
        'qos': {
            'reliability': _none_if_unknown(endpoint.reliability),
            'durability': _none_if_unknown(endpoint.durability),
            'history': _none_if_unknown(endpoint.history),
            'depth': endpoint.depth,
            'deadline': endpoint.deadline,
            'lifespan': endpoint.lifespan,
            'liveliness': _none_if_unknown(endpoint.liveliness),
            'liveliness_lease_duration': endpoint.liveliness_lease_duration,
        },
    }


def _issue_values(issue: CompatibilityIssue) -> tuple[Optional[Any], Optional[Any]]:
    if issue.policy == 'reliability':
        return issue.publisher.reliability, issue.subscriber.reliability
    if issue.policy == 'durability':
        return issue.publisher.durability, issue.subscriber.durability
    if issue.policy == 'deadline':
        return issue.publisher.deadline, issue.subscriber.deadline
    if issue.policy == 'liveliness':
        return issue.publisher.liveliness, issue.subscriber.liveliness
    if issue.policy == 'liveliness_lease_duration':
        return (
            issue.publisher.liveliness_lease_duration,
            issue.subscriber.liveliness_lease_duration,
        )
    return None, None


def issue_to_dict(issue: CompatibilityIssue) -> dict:
    publisher_value, subscriber_value = _issue_values(issue)
    return {
        'policy': issue.policy,
        'publisher': issue.publisher.full_node_name,
        'subscriber': issue.subscriber.full_node_name,
        'publisher_value': _none_if_unknown(publisher_value),
        'subscriber_value': _none_if_unknown(subscriber_value),
        'message': issue.message,
        'suggested_fix': issue.suggested_fix,
    }


def diagnosis_to_dict(diagnosis: TopicDiagnosis, mode: Optional[str] = None) -> dict:
    result = {}
    if mode is not None:
        result['mode'] = mode

    result.update(
        {
            'topic': diagnosis.topic_name,
            'topic_types': diagnosis.topic_types,
            'compatible': diagnosis.compatibility.compatible,
            'publishers': [
                endpoint_to_dict(endpoint)
                for endpoint in diagnosis.publishers
            ],
            'subscribers': [
                endpoint_to_dict(endpoint)
                for endpoint in diagnosis.subscribers
            ],
            'issues': [
                issue_to_dict(issue)
                for issue in diagnosis.compatibility.issues
            ],
        }
    )
    return result


def system_scan_to_dict(
    scan_result: SystemScanResult,
    show_compatible: bool = False,
) -> dict:
    reported_diagnoses = [
        diagnosis for diagnosis in scan_result.diagnoses
        if show_compatible or diagnosis.has_issues
    ]
    return {
        'mode': 'all_topics',
        'summary': {
            'scanned_topics': scan_result.scanned_topic_count,
            'topics_with_publishers_and_subscribers': (
                scan_result.topics_with_publishers_and_subscribers_count
            ),
            'topics_with_qos_issues': scan_result.topics_with_issues_count,
            'reported_topics': len(reported_diagnoses),
        },
        'topics': [
            diagnosis_to_dict(diagnosis)
            for diagnosis in reported_diagnoses
        ],
    }


def format_json(data: dict) -> str:
    return json.dumps(data, indent=2, sort_keys=True)
