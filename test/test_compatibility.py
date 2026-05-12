from ros2_qos_doctor.compatibility import EndpointQoS, check_compatibility, normalize_policy


def endpoint(reliability='reliable', durability='volatile'):
    return EndpointQoS(
        node_name='node',
        reliability=reliability,
        durability=durability,
        history='keep_last',
        depth=10,
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


def test_normalize_policy_handles_ros_enum_strings():
    assert normalize_policy('QoSReliabilityPolicy.RELIABLE') == 'reliable'
    assert normalize_policy('QoSDurabilityPolicy.TRANSIENT_LOCAL') == 'transient_local'
    assert normalize_policy('RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT') == 'best_effort'
    assert normalize_policy('RMW_QOS_POLICY_DURABILITY_TRANSIENT_LOCAL') == 'transient_local'
