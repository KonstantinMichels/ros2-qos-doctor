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
    liveliness: Optional[str] = None
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
    message: str
    suggested_fix: str


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


COMPATIBILITY_RULES = (
    CompatibilityRule(
        policy='reliability',
        is_incompatible=lambda publisher, subscriber: (
            publisher.reliability == 'best_effort'
            and subscriber.reliability == 'reliable'
        ),
        message=(
            'Reliability mismatch. The subscriber requests RELIABLE delivery, '
            'but the publisher only offers BEST_EFFORT delivery.'
        ),
        suggested_fix='Set the subscriber reliability to BEST_EFFORT.',
    ),
    CompatibilityRule(
        policy='durability',
        is_incompatible=lambda publisher, subscriber: (
            publisher.durability == 'volatile'
            and subscriber.durability == 'transient_local'
        ),
        message=(
            'Durability mismatch. The subscriber requests TRANSIENT_LOCAL durability, '
            'but the publisher only offers VOLATILE durability.'
        ),
        suggested_fix='Set the subscriber durability to VOLATILE.',
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
                    message=rule.message,
                    suggested_fix=rule.suggested_fix,
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
