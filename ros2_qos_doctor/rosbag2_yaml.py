from typing import Iterable, Optional

from ros2_qos_doctor.compatibility import CompatibilityIssue


def _base_override_from_issue(issue: CompatibilityIssue) -> dict:
    override = {}
    subscriber = issue.subscriber

    if subscriber.reliability != 'unknown':
        override['reliability'] = subscriber.reliability
    if subscriber.durability != 'unknown':
        override['durability'] = subscriber.durability
    if subscriber.history != 'unknown':
        override['history'] = subscriber.history
    if subscriber.depth is not None:
        override['depth'] = subscriber.depth

    return override


def _apply_policy_fix(override: dict, issue: CompatibilityIssue) -> None:
    if issue.policy == 'reliability':
        override['reliability'] = issue.publisher.reliability
    elif issue.policy == 'durability':
        override['durability'] = issue.publisher.durability


def suggest_rosbag2_override(
    topic_name: str,
    issues: Iterable[CompatibilityIssue],
) -> Optional[dict]:
    issue_list = list(issues)
    if not issue_list:
        return None

    target_issue = issue_list[0]
    override = _base_override_from_issue(target_issue)
    for issue in issue_list:
        same_pair = (
            issue.publisher == target_issue.publisher
            and issue.subscriber == target_issue.subscriber
        )
        if same_pair:
            _apply_policy_fix(override, issue)

    override.setdefault('history', 'keep_last')
    override.setdefault('depth', 10)
    return {topic_name: override}


def format_rosbag2_override_yaml(topic_name: str, issues: Iterable[CompatibilityIssue]) -> str:
    suggestion = suggest_rosbag2_override(topic_name, issues)
    if suggestion is None:
        return ''

    topic_override = suggestion[topic_name]
    lines = [f'{topic_name}:']
    for key in ('reliability', 'durability', 'history', 'depth'):
        if key in topic_override:
            lines.append(f'  {key}: {topic_override[key]}')
    return '\n'.join(lines)
