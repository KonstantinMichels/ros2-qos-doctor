from typing import Iterable, List

from ros2_qos_doctor.compatibility import CompatibilityIssue, CompatibilityReport, EndpointQoS
from ros2_qos_doctor.diagnosis import SystemScanResult, TopicDiagnosis
from ros2_qos_doctor.explanations import problem_lines, suggested_fix_lines
from ros2_qos_doctor.rosbag2_yaml import format_rosbag2_override_yaml


def _endpoint_lines(endpoint: EndpointQoS) -> List[str]:
    lines = [
        f'  - node: {endpoint.full_node_name}',
        f'    namespace: {endpoint.node_namespace or "/"}',
    ]
    if endpoint.topic_type:
        lines.append(f'    type: {endpoint.topic_type}')
    lines.extend(
        [
            f'    reliability: {endpoint.reliability}',
            f'    durability: {endpoint.durability}',
            f'    history: {endpoint.history}',
            f'    depth: {endpoint.depth if endpoint.depth is not None else "unknown"}',
            f'    deadline: {_format_duration(endpoint.deadline)}',
            f'    lifespan: {_format_duration(endpoint.lifespan)}',
        ]
    )
    if endpoint.liveliness:
        lines.append(f'    liveliness: {endpoint.liveliness}')
    lines.append(
        '    liveliness_lease_duration: '
        f'{_format_duration(endpoint.liveliness_lease_duration)}'
    )
    return lines


def _format_endpoints(title: str, endpoints: Iterable[EndpointQoS]) -> List[str]:
    endpoint_list = list(endpoints)
    lines = [f'{title}:']
    if not endpoint_list:
        lines.append('  none discovered')
        return lines

    for endpoint in endpoint_list:
        lines.extend(_endpoint_lines(endpoint))
    return lines


def format_report(
    topic_name: str,
    publishers: Iterable[EndpointQoS],
    subscribers: Iterable[EndpointQoS],
    report: CompatibilityReport,
    include_rosbag2_yaml: bool = False,
) -> str:
    lines: List[str] = ['ros2-qos-doctor', '', f'Topic: {topic_name}', '']
    lines.extend(_format_endpoints('Publishers', publishers))
    lines.append('')
    lines.extend(_format_endpoints('Subscribers', subscribers))
    lines.extend(['', 'Compatibility:'])
    lines.append('  Compatible' if report.compatible else '  Incompatible')

    if report.issues:
        lines.extend(['', 'Problem:'])
        for problem in problem_lines(report.issues):
            lines.append(f'  {problem}')

        lines.extend(['', 'Suggested fix:'])
        for fix in suggested_fix_lines(report.issues):
            lines.append(f'  {fix}')

    if include_rosbag2_yaml and report.issues:
        yaml_text = format_rosbag2_override_yaml(topic_name, report.issues)
        if yaml_text:
            lines.extend(['', 'rosbag2 override suggestion:'])
            lines.extend(f'  {line}' for line in yaml_text.splitlines())

    return '\n'.join(lines)


def format_topic_diagnosis(
    diagnosis: TopicDiagnosis,
    include_rosbag2_yaml: bool = False,
) -> str:
    return format_report(
        diagnosis.topic_name,
        diagnosis.publishers,
        diagnosis.subscribers,
        diagnosis.compatibility,
        include_rosbag2_yaml=include_rosbag2_yaml,
    )


def _policy_label(policy: str) -> str:
    return policy.replace('_', ' ').title()


def _policy_value(value: str) -> str:
    return value.upper()


def _format_duration(value: int | None) -> str:
    if value in (None, 0):
        return 'default'
    return f'{value} ns'


def _issue_detail_lines(issue: CompatibilityIssue) -> List[str]:
    if issue.policy == 'reliability':
        return [
            '   Reliability mismatch:',
            (
                f'   Publisher {issue.publisher.full_node_name} offers '
                f'{_policy_value(issue.publisher.reliability)}'
            ),
            (
                f'   Subscriber {issue.subscriber.full_node_name} requests '
                f'{_policy_value(issue.subscriber.reliability)}'
            ),
        ]
    if issue.policy == 'durability':
        return [
            '   Durability mismatch:',
            (
                f'   Publisher {issue.publisher.full_node_name} offers '
                f'{_policy_value(issue.publisher.durability)}'
            ),
            (
                f'   Subscriber {issue.subscriber.full_node_name} requests '
                f'{_policy_value(issue.subscriber.durability)}'
            ),
        ]
    if issue.policy == 'deadline':
        return [
            '   Deadline mismatch:',
            (
                f'   Publisher {issue.publisher.full_node_name} offers '
                f'{_format_duration(issue.publisher.deadline)}'
            ),
            (
                f'   Subscriber {issue.subscriber.full_node_name} requests '
                f'{_format_duration(issue.subscriber.deadline)}'
            ),
        ]
    if issue.policy == 'liveliness':
        return [
            '   Liveliness mismatch:',
            (
                f'   Publisher {issue.publisher.full_node_name} offers '
                f'{_policy_value(issue.publisher.liveliness or "unknown")}'
            ),
            (
                f'   Subscriber {issue.subscriber.full_node_name} requests '
                f'{_policy_value(issue.subscriber.liveliness or "unknown")}'
            ),
        ]
    if issue.policy == 'liveliness_lease_duration':
        return [
            '   Liveliness lease duration mismatch:',
            (
                f'   Publisher {issue.publisher.full_node_name} offers '
                f'{_format_duration(issue.publisher.liveliness_lease_duration)}'
            ),
            (
                f'   Subscriber {issue.subscriber.full_node_name} requests '
                f'{_format_duration(issue.subscriber.liveliness_lease_duration)}'
            ),
        ]

    return [f'   {_policy_label(issue.policy)} mismatch:', f'   {issue.message}']


def _format_issue_topic(diagnosis: TopicDiagnosis) -> List[str]:
    lines = [f'❌ {diagnosis.topic_name}']
    for index, issue in enumerate(diagnosis.compatibility.issues):
        if index:
            lines.append('')
        lines.extend(_issue_detail_lines(issue))
        lines.extend(['', '   Suggested fix:', f'   {issue.suggested_fix}'])
    return lines


def _format_rosbag2_yaml_for_scan(diagnosis: TopicDiagnosis) -> List[str]:
    yaml_text = format_rosbag2_override_yaml(
        diagnosis.topic_name,
        diagnosis.compatibility.issues,
    )
    if not yaml_text:
        return []

    lines = ['', '   rosbag2 override suggestion:']
    lines.extend(f'   {line}' for line in yaml_text.splitlines())
    return lines


def _format_compatible_topic(diagnosis: TopicDiagnosis) -> List[str]:
    lines = [f'✅ {diagnosis.topic_name}']
    if not diagnosis.publishers:
        lines.append('   No publishers found.')
    elif not diagnosis.subscribers:
        lines.append('   No subscribers found.')
    else:
        lines.append('   Compatible publisher/subscriber QoS pairs found.')
    return lines


def format_system_scan(
    scan_result: SystemScanResult,
    show_compatible: bool = False,
    include_rosbag2_yaml: bool = False,
) -> str:
    lines: List[str] = [
        'ros2-qos-doctor system scan',
        '',
        f'Scanned topics: {scan_result.scanned_topic_count}',
        (
            'Topics with publishers and subscribers: '
            f'{scan_result.topics_with_publishers_and_subscribers_count}'
        ),
        f'Topics with QoS issues: {scan_result.topics_with_issues_count}',
        '',
    ]

    issue_diagnoses = [
        diagnosis for diagnosis in scan_result.diagnoses
        if diagnosis.has_issues
    ]

    if not issue_diagnoses:
        lines.append('✅ No QoS incompatibilities detected.')
    else:
        for index, diagnosis in enumerate(issue_diagnoses):
            if index:
                lines.append('')
            lines.extend(_format_issue_topic(diagnosis))
            if include_rosbag2_yaml:
                lines.extend(_format_rosbag2_yaml_for_scan(diagnosis))

    if show_compatible:
        compatible_diagnoses = [
            diagnosis for diagnosis in scan_result.diagnoses
            if not diagnosis.has_issues
        ]
        for diagnosis in compatible_diagnoses:
            lines.append('')
            lines.extend(_format_compatible_topic(diagnosis))

    return '\n'.join(lines)
