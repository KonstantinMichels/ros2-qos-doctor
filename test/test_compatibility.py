import pytest

from ros2_qos_doctor.compatibility import (
    EndpointQoS,
    check_compatibility,
    duration_to_nanoseconds,
    normalize_policy,
)


def endpoint(reliability='reliable', durability='volatile', **kwargs):
    return EndpointQoS(
        node_name='node',
        reliability=reliability,
        durability=durability,
        history='keep_last',
        depth=10,
        **kwargs,
    )


def assert_compatible(pub_reliability, sub_reliability, pub_durability, sub_durability):
    report = check_compatibility(
        [endpoint(pub_reliability, pub_durability)],
        [endpoint(sub_reliability, sub_durability)],
    )
    assert report.compatible
    assert report.issues == []


def assert_incompatible(pub_reliability, sub_reliability, pub_durability, sub_durability, policy):
    report = check_compatibility(
        [endpoint(pub_reliability, pub_durability)],
        [endpoint(sub_reliability, sub_durability)],
    )
    assert not report.compatible
    assert any(issue.policy == policy for issue in report.issues)


def policies_for(publisher, subscriber):
    report = check_compatibility([publisher], [subscriber])
    return {issue.policy for issue in report.issues}


@pytest.mark.parametrize(
    ('publisher_reliability', 'subscriber_reliability', 'expected_compatible'),
    [
        ('best_effort', 'best_effort', True),
        ('best_effort', 'reliable', False),
        ('reliable', 'best_effort', True),
        ('reliable', 'reliable', True),
    ],
)
def test_official_reliability_compatibility_table(
    publisher_reliability,
    subscriber_reliability,
    expected_compatible,
):
    report = check_compatibility(
        [endpoint(reliability=publisher_reliability)],
        [endpoint(reliability=subscriber_reliability)],
    )

    assert report.compatible is expected_compatible
    if expected_compatible:
        assert report.issues == []
    else:
        assert {issue.policy for issue in report.issues} == {'reliability'}


@pytest.mark.parametrize(
    ('publisher_durability', 'subscriber_durability', 'expected_compatible'),
    [
        ('volatile', 'volatile', True),
        ('volatile', 'transient_local', False),
        ('transient_local', 'volatile', True),
        ('transient_local', 'transient_local', True),
    ],
)
def test_official_durability_compatibility_table(
    publisher_durability,
    subscriber_durability,
    expected_compatible,
):
    report = check_compatibility(
        [endpoint(durability=publisher_durability)],
        [endpoint(durability=subscriber_durability)],
    )

    assert report.compatible is expected_compatible
    if expected_compatible:
        assert report.issues == []
    else:
        assert {issue.policy for issue in report.issues} == {'durability'}


@pytest.mark.parametrize(
    ('publisher_deadline', 'subscriber_deadline', 'expected_compatible'),
    [
        (0, 0, True),
        (0, 1_000_000_000, False),
        (1_000_000_000, 0, True),
        (1_000_000_000, 1_000_000_000, True),
        (1_000_000_000, 2_000_000_000, True),
        (2_000_000_000, 1_000_000_000, False),
    ],
)
def test_official_deadline_compatibility_table(
    publisher_deadline,
    subscriber_deadline,
    expected_compatible,
):
    report = check_compatibility(
        [endpoint(deadline=publisher_deadline)],
        [endpoint(deadline=subscriber_deadline)],
    )

    assert report.compatible is expected_compatible
    if expected_compatible:
        assert report.issues == []
    else:
        assert {issue.policy for issue in report.issues} == {'deadline'}


@pytest.mark.parametrize(
    ('publisher_liveliness', 'subscriber_liveliness', 'expected_compatible'),
    [
        ('automatic', 'automatic', True),
        ('automatic', 'manual_by_topic', False),
        ('manual_by_topic', 'automatic', True),
        ('manual_by_topic', 'manual_by_topic', True),
    ],
)
def test_official_liveliness_compatibility_table(
    publisher_liveliness,
    subscriber_liveliness,
    expected_compatible,
):
    report = check_compatibility(
        [endpoint(liveliness=publisher_liveliness)],
        [endpoint(liveliness=subscriber_liveliness)],
    )

    assert report.compatible is expected_compatible
    if expected_compatible:
        assert report.issues == []
    else:
        assert {issue.policy for issue in report.issues} == {'liveliness'}


@pytest.mark.parametrize(
    ('publisher_lease_duration', 'subscriber_lease_duration', 'expected_compatible'),
    [
        (0, 0, True),
        (0, 1_000_000_000, False),
        (1_000_000_000, 0, True),
        (1_000_000_000, 1_000_000_000, True),
        (1_000_000_000, 2_000_000_000, True),
        (2_000_000_000, 1_000_000_000, False),
    ],
)
def test_official_liveliness_lease_duration_compatibility_table(
    publisher_lease_duration,
    subscriber_lease_duration,
    expected_compatible,
):
    report = check_compatibility(
        [endpoint(liveliness_lease_duration=publisher_lease_duration)],
        [endpoint(liveliness_lease_duration=subscriber_lease_duration)],
    )

    assert report.compatible is expected_compatible
    if expected_compatible:
        assert report.issues == []
    else:
        assert {issue.policy for issue in report.issues} == {
            'liveliness_lease_duration'
        }


def test_reliability_best_effort_publisher_reliable_subscriber_is_incompatible():
    assert_incompatible('best_effort', 'reliable', 'volatile', 'volatile', 'reliability')


def test_reliability_reliable_publisher_best_effort_subscriber_is_compatible():
    assert_compatible('reliable', 'best_effort', 'volatile', 'volatile')


def test_reliability_matching_policies_are_compatible():
    assert_compatible('reliable', 'reliable', 'volatile', 'volatile')
    assert_compatible('best_effort', 'best_effort', 'volatile', 'volatile')


def test_durability_volatile_publisher_transient_local_subscriber_is_incompatible():
    assert_incompatible('reliable', 'reliable', 'volatile', 'transient_local', 'durability')


def test_durability_transient_local_publisher_volatile_subscriber_is_compatible():
    assert_compatible('reliable', 'reliable', 'transient_local', 'volatile')


def test_durability_matching_policies_are_compatible():
    assert_compatible('reliable', 'reliable', 'volatile', 'volatile')
    assert_compatible('reliable', 'reliable', 'transient_local', 'transient_local')


def test_multiple_issues_are_reported_for_one_pair():
    report = check_compatibility(
        [endpoint('best_effort', 'volatile')],
        [endpoint('reliable', 'transient_local')],
    )

    assert not report.compatible
    assert {issue.policy for issue in report.issues} == {'reliability', 'durability'}


def test_deadline_default_publisher_finite_subscriber_is_incompatible():
    report = check_compatibility(
        [endpoint(deadline=0)],
        [endpoint(deadline=1_000_000_000)],
    )

    assert not report.compatible
    assert {issue.policy for issue in report.issues} == {'deadline'}


def test_deadline_publisher_must_offer_interval_no_greater_than_subscriber_request():
    compatible = check_compatibility(
        [endpoint(deadline=1_000_000_000)],
        [endpoint(deadline=2_000_000_000)],
    )
    incompatible = check_compatibility(
        [endpoint(deadline=2_000_000_000)],
        [endpoint(deadline=1_000_000_000)],
    )

    assert compatible.compatible
    assert not incompatible.compatible
    assert {issue.policy for issue in incompatible.issues} == {'deadline'}


def test_liveliness_automatic_publisher_manual_subscriber_is_incompatible():
    report = check_compatibility(
        [endpoint(liveliness='automatic')],
        [endpoint(liveliness='manual_by_topic')],
    )

    assert not report.compatible
    assert {issue.policy for issue in report.issues} == {'liveliness'}


def test_liveliness_manual_publisher_automatic_subscriber_is_compatible():
    report = check_compatibility(
        [endpoint(liveliness='manual_by_topic')],
        [endpoint(liveliness='automatic')],
    )

    assert report.compatible


def test_liveliness_lease_duration_uses_requested_offered_duration_rule():
    compatible = check_compatibility(
        [endpoint(liveliness_lease_duration=1_000_000_000)],
        [endpoint(liveliness_lease_duration=2_000_000_000)],
    )
    incompatible = check_compatibility(
        [endpoint(liveliness_lease_duration=2_000_000_000)],
        [endpoint(liveliness_lease_duration=1_000_000_000)],
    )

    assert compatible.compatible
    assert not incompatible.compatible
    assert {issue.policy for issue in incompatible.issues} == {
        'liveliness_lease_duration'
    }


def test_lifespan_does_not_create_a_hard_compatibility_issue():
    report = check_compatibility(
        [endpoint(lifespan=1_000_000_000)],
        [endpoint(lifespan=2_000_000_000)],
    )

    assert report.compatible


def test_normalize_policy_handles_ros_enum_strings():
    assert normalize_policy('QoSReliabilityPolicy.RELIABLE') == 'reliable'
    assert normalize_policy('QoSDurabilityPolicy.TRANSIENT_LOCAL') == 'transient_local'
    assert normalize_policy('RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT') == 'best_effort'
    assert normalize_policy('RMW_QOS_POLICY_DURABILITY_TRANSIENT_LOCAL') == 'transient_local'


def test_duration_to_nanoseconds_handles_ints_and_unknown_values():
    assert duration_to_nanoseconds(123) == 123
    assert duration_to_nanoseconds(None) is None
    assert duration_to_nanoseconds('not-a-duration') is None
