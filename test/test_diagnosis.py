from ros2_qos_doctor.compatibility import EndpointQoS, check_compatibility
from ros2_qos_doctor.diagnosis import TopicDiagnosis, build_system_scan_result


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


def test_build_system_scan_result_counts_topics_and_issues():
    incompatible = diagnosis(
        '/qos_demo/reliability',
        [endpoint('best_effort_publisher', reliability='best_effort')],
        [endpoint('reliable_subscriber', reliability='reliable')],
    )
    compatible = diagnosis(
        '/qos_demo/reliability_compatible',
        [endpoint('reliable_publisher', reliability='reliable')],
        [endpoint('best_effort_subscriber', reliability='best_effort')],
    )
    publisher_only = diagnosis('/publisher_only', [endpoint('talker')], [])

    scan_result = build_system_scan_result([incompatible, compatible, publisher_only])

    assert scan_result.scanned_topic_count == 3
    assert scan_result.topics_with_publishers_and_subscribers_count == 2
    assert scan_result.topics_with_issues_count == 1
    assert scan_result.diagnoses == [incompatible, compatible, publisher_only]
