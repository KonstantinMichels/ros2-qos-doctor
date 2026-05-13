from ros2_qos_doctor.compatibility import EndpointQoS, check_compatibility
from ros2_qos_doctor.diagnosis import TopicDiagnosis, build_system_scan_result
from ros2_qos_doctor.formatting import format_system_scan


def endpoint(node_name, reliability='reliable', durability='volatile'):
    return EndpointQoS(
        node_name=node_name,
        reliability=reliability,
        durability=durability,
        history='keep_last',
        depth=10,
    )


def diagnosis(topic_name, publishers, subscribers):
    return TopicDiagnosis(
        topic_name=topic_name,
        topic_types=['std_msgs/msg/String'],
        publishers=publishers,
        subscribers=subscribers,
        compatibility=check_compatibility(publishers, subscribers),
    )


def test_format_system_scan_only_shows_incompatible_topics_by_default():
    incompatible = diagnosis(
        '/qos_demo/reliability',
        [endpoint('best_effort_publisher', reliability='best_effort')],
        [endpoint('reliable_subscriber', reliability='reliable')],
    )
    compatible = diagnosis(
        '/qos_demo/reliability_compatible',
        [endpoint('reliable_publisher')],
        [endpoint('best_effort_subscriber', reliability='best_effort')],
    )

    output = format_system_scan(build_system_scan_result([incompatible, compatible]))

    assert 'Topics with QoS issues: 1' in output
    assert '❌ /qos_demo/reliability' in output
    assert 'Publisher /best_effort_publisher offers BEST_EFFORT' in output
    assert 'Subscriber /reliable_subscriber requests RELIABLE' in output
    assert '/qos_demo/reliability_compatible' not in output


def test_format_system_scan_can_show_compatible_topics():
    compatible = diagnosis(
        '/qos_demo/reliability_compatible',
        [endpoint('reliable_publisher')],
        [endpoint('best_effort_subscriber', reliability='best_effort')],
    )

    output = format_system_scan(
        build_system_scan_result([compatible]),
        show_compatible=True,
    )

    assert '✅ No QoS incompatibilities detected.' in output
    assert '✅ /qos_demo/reliability_compatible' in output
    assert 'Compatible publisher/subscriber QoS pairs found.' in output


def test_format_system_scan_reports_missing_subscribers_when_showing_compatible_topics():
    publisher_only = diagnosis('/publisher_only', [endpoint('talker')], [])

    output = format_system_scan(
        build_system_scan_result([publisher_only]),
        show_compatible=True,
    )

    assert '✅ /publisher_only' in output
    assert 'No subscribers found.' in output


def test_format_system_scan_can_include_rosbag2_yaml_for_issue_topics():
    incompatible = diagnosis(
        '/qos_demo/reliability',
        [endpoint('best_effort_publisher', reliability='best_effort')],
        [endpoint('reliable_subscriber', reliability='reliable')],
    )

    output = format_system_scan(
        build_system_scan_result([incompatible]),
        include_rosbag2_yaml=True,
    )

    assert 'rosbag2 override suggestion:' in output
    assert '   /qos_demo/reliability:' in output
    assert '     reliability: best_effort' in output
