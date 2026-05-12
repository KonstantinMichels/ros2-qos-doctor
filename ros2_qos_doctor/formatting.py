from typing import Iterable, List

from ros2_qos_doctor.compatibility import CompatibilityReport, EndpointQoS
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
        ]
    )
    if endpoint.liveliness:
        lines.append(f'    liveliness: {endpoint.liveliness}')
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
