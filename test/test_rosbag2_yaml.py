from ros2_qos_doctor.compatibility import EndpointQoS, check_compatibility
from ros2_qos_doctor.rosbag2_yaml import format_rosbag2_override_yaml


def test_rosbag2_override_uses_publisher_policy_for_durability_mismatch():
    publisher = EndpointQoS(
        node_name='talker',
        reliability='reliable',
        durability='volatile',
        history='keep_last',
        depth=100,
    )
    subscriber = EndpointQoS(
        node_name='rosbag2_recorder',
        reliability='reliable',
        durability='transient_local',
        history='keep_last',
        depth=100,
    )
    report = check_compatibility([publisher], [subscriber])

    assert format_rosbag2_override_yaml('/tf', report.issues) == '\n'.join(
        [
            '/tf:',
            '  reliability: reliable',
            '  durability: volatile',
            '  history: keep_last',
            '  depth: 100',
        ]
    )


def test_rosbag2_override_uses_publisher_policy_for_reliability_mismatch():
    publisher = EndpointQoS(
        node_name='camera',
        reliability='best_effort',
        durability='volatile',
        history='keep_last',
        depth=5,
    )
    subscriber = EndpointQoS(
        node_name='rosbag2_recorder',
        reliability='reliable',
        durability='volatile',
        history='keep_last',
        depth=10,
    )
    report = check_compatibility([publisher], [subscriber])

    assert format_rosbag2_override_yaml('/image_raw', report.issues) == '\n'.join(
        [
            '/image_raw:',
            '  reliability: best_effort',
            '  durability: volatile',
            '  history: keep_last',
            '  depth: 10',
        ]
    )


def test_rosbag2_override_uses_first_pair_instead_of_blending_multiple_pairs():
    first_publisher = EndpointQoS(
        node_name='camera_a',
        reliability='best_effort',
        durability='volatile',
        history='keep_last',
        depth=5,
    )
    first_subscriber = EndpointQoS(
        node_name='recorder_a',
        reliability='reliable',
        durability='volatile',
        history='keep_last',
        depth=10,
    )
    second_publisher = EndpointQoS(
        node_name='camera_b',
        reliability='reliable',
        durability='volatile',
        history='keep_last',
        depth=20,
    )
    second_subscriber = EndpointQoS(
        node_name='recorder_b',
        reliability='reliable',
        durability='transient_local',
        history='keep_last',
        depth=20,
    )
    report = check_compatibility(
        [first_publisher, second_publisher],
        [first_subscriber, second_subscriber],
    )

    assert format_rosbag2_override_yaml('/mixed', report.issues) == '\n'.join(
        [
            '/mixed:',
            '  reliability: best_effort',
            '  durability: volatile',
            '  history: keep_last',
            '  depth: 10',
        ]
    )
