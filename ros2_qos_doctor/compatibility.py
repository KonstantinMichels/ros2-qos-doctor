from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, List, Optional


class EndpointKind(str, Enum):
    PUBLISHER = 'publisher'
    SUBSCRIBER = 'subscriber'


@dataclass(frozen=True)
class EndpointQoS:
    node_name: str
    node_namespace: str = '/'
    topic_type: Optional[str] = None
    reliability: str = 'unknown'
    durability: str = 'unknown'
    history: str = 'unknown'
    depth: Optional[int] = None
    deadline: Optional[int] = None
    lifespan: Optional[int] = None
    liveliness: Optional[str] = None
    liveliness_lease_duration: Optional[int] = None
    endpoint_kind: Optional[EndpointKind] = None

    @property
    def full_node_name(self) -> str:
        namespace = self.node_namespace or '/'
        if namespace == '/':
            return f'/{self.node_name.lstrip("/")}'
        return f'{namespace.rstrip("/")}/{self.node_name.lstrip("/")}'


@dataclass(frozen=True)
class CompatibilityIssue:
    policy: str
    publisher: EndpointQoS
    subscriber: EndpointQoS
    message: str
    suggested_fix: str


@dataclass(frozen=True)
class CompatibilityReport:
    compatible: bool
    issues: List[CompatibilityIssue]


@dataclass(frozen=True)
class CompatibilityRule:
    policy: str
    is_incompatible: Callable[[EndpointQoS, EndpointQoS], bool]
    message: Callable[[EndpointQoS, EndpointQoS], str]
    suggested_fix: Callable[[EndpointQoS, EndpointQoS], str]


def normalize_policy(value: object) -> str:
    if value is None:
        return 'unknown'

    text = getattr(value, 'name', None) or str(value)
    if '.' in text:
        text = text.rsplit('.', 1)[-1]

    text = text.lower()
    for prefix in ('rmw_qos_policy_', 'qos_policy_'):
        if text.startswith(prefix):
            text = text[len(prefix):]

    for category in ('reliability_', 'durability_', 'history_', 'liveliness_'):
        if text.startswith(category):
            text = text[len(category):]

    return text


def duration_to_nanoseconds(value: object) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value

    nanoseconds = getattr(value, 'nanoseconds', None)
    if nanoseconds is not None:
        return nanoseconds

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _is_default_duration(value: Optional[int]) -> bool:
    return value in (None, 0)


def _duration_is_incompatible(
    publisher_value: Optional[int],
    subscriber_value: Optional[int],
) -> bool:
    if _is_default_duration(subscriber_value):
        return False
    if _is_default_duration(publisher_value):
        return True
    return publisher_value > subscriber_value


def _format_duration(value: Optional[int]) -> str:
    if _is_default_duration(value):
        return 'DEFAULT'
    return f'{value} ns'


def _constant_message(message: str) -> Callable[[EndpointQoS, EndpointQoS], str]:
    return lambda _publisher, _subscriber: message


def _constant_fix(fix: str) -> Callable[[EndpointQoS, EndpointQoS], str]:
    return lambda _publisher, _subscriber: fix


COMPATIBILITY_RULES = (
    CompatibilityRule(
        policy='reliability',
        is_incompatible=lambda publisher, subscriber: (
            publisher.reliability == 'best_effort'
            and subscriber.reliability == 'reliable'
        ),
        message=_constant_message(
            'Reliability mismatch. The subscriber requests RELIABLE delivery, '
            'but the publisher only offers BEST_EFFORT delivery.'
        ),
        suggested_fix=_constant_fix('Set the subscriber reliability to BEST_EFFORT.'),
    ),
    CompatibilityRule(
        policy='durability',
        is_incompatible=lambda publisher, subscriber: (
            publisher.durability == 'volatile'
            and subscriber.durability == 'transient_local'
        ),
        message=_constant_message(
            'Durability mismatch. The subscriber requests TRANSIENT_LOCAL durability, '
            'but the publisher only offers VOLATILE durability.'
        ),
        suggested_fix=_constant_fix('Set the subscriber durability to VOLATILE.'),
    ),
    CompatibilityRule(
        policy='deadline',
        is_incompatible=lambda publisher, subscriber: _duration_is_incompatible(
            publisher.deadline,
            subscriber.deadline,
        ),
        message=lambda publisher, subscriber: (
            'Deadline mismatch. The subscriber requests a maximum interval of '
            f'{_format_duration(subscriber.deadline)}, but the publisher only '
            f'offers {_format_duration(publisher.deadline)}.'
        ),
        suggested_fix=lambda publisher, _subscriber: (
            'Set the subscriber deadline to DEFAULT or at least '
            f'{_format_duration(publisher.deadline)}.'
        ),
    ),
    CompatibilityRule(
        policy='liveliness',
        is_incompatible=lambda publisher, subscriber: (
            publisher.liveliness == 'automatic'
            and subscriber.liveliness == 'manual_by_topic'
        ),
        message=_constant_message(
            'Liveliness mismatch. The subscriber requests MANUAL_BY_TOPIC '
            'liveliness, but the publisher only offers AUTOMATIC liveliness.'
        ),
        suggested_fix=_constant_fix(
            'Set the subscriber liveliness to AUTOMATIC.'
        ),
    ),
    CompatibilityRule(
        policy='liveliness_lease_duration',
        is_incompatible=lambda publisher, subscriber: _duration_is_incompatible(
            publisher.liveliness_lease_duration,
            subscriber.liveliness_lease_duration,
        ),
        message=lambda publisher, subscriber: (
            'Liveliness lease duration mismatch. The subscriber requests a '
            f'lease duration of {_format_duration(subscriber.liveliness_lease_duration)}, '
            'but the publisher only offers '
            f'{_format_duration(publisher.liveliness_lease_duration)}.'
        ),
        suggested_fix=lambda publisher, _subscriber: (
            'Set the subscriber liveliness lease duration to DEFAULT or at least '
            f'{_format_duration(publisher.liveliness_lease_duration)}.'
        ),
    ),
)


def check_pair_compatibility(
    publisher: EndpointQoS,
    subscriber: EndpointQoS,
) -> List[CompatibilityIssue]:
    issues: List[CompatibilityIssue] = []

    for rule in COMPATIBILITY_RULES:
        if rule.is_incompatible(publisher, subscriber):
            issues.append(
                CompatibilityIssue(
                    policy=rule.policy,
                    publisher=publisher,
                    subscriber=subscriber,
                    message=rule.message(publisher, subscriber),
                    suggested_fix=rule.suggested_fix(publisher, subscriber),
                )
            )

    return issues


def check_compatibility(
    publishers: Iterable[EndpointQoS],
    subscribers: Iterable[EndpointQoS],
) -> CompatibilityReport:
    issues: List[CompatibilityIssue] = []

    for publisher in publishers:
        for subscriber in subscribers:
            issues.extend(check_pair_compatibility(publisher, subscriber))

    return CompatibilityReport(compatible=not issues, issues=issues)
