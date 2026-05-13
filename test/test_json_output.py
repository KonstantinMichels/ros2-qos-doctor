import json

from ros2_qos_doctor.compatibility import EndpointQoS, check_compatibility
from ros2_qos_doctor.diagnosis import TopicDiagnosis, build_system_scan_result
from ros2_qos_doctor.json_output import (
    diagnosis_to_dict,
    format_json,
    system_scan_to_dict,
)


def endpoint(node_name, reliability='reliable', durability='volatile'):
    return EndpointQoS(
        node_name=node_name,
        node_namespace='/',
        topic_type='std_msgs/msg/String',
        reliability=reliability,
        durability=durability,
        history='keep_last',
        depth=10,
        deadline=0,
        lifespan=0,
        liveliness='automatic',
        liveliness_lease_duration=0,
    )


def diagnosis(topic_name, publishers, subscribers):
    return TopicDiagnosis(
        topic_name=topic_name,
        topic_types=['std_msgs/msg/String'],
        publishers=publishers,
        subscribers=subscribers,
        compatibility=check_compatibility(publishers, subscribers),
    )


def parse_json(data):
    return json.loads(format_json(data))


def test_single_topic_json_reliability_issue_is_parseable():
    data = diagnosis_to_dict(
        diagnosis(
            '/qos_demo/reliability',
            [endpoint('best_effort_publisher', reliability='best_effort')],
            [endpoint('reliable_subscriber', reliability='reliable')],
        ),
        mode='single_topic',
    )

    parsed = parse_json(data)

    assert parsed['mode'] == 'single_topic'
    assert parsed['topic'] == '/qos_demo/reliability'
    assert parsed['compatible'] is False
    assert parsed['issues'][0]['policy'] == 'reliability'
    assert parsed['issues'][0]['publisher_value'] == 'best_effort'
    assert parsed['issues'][0]['subscriber_value'] == 'reliable'


def test_single_topic_json_durability_issue_is_parseable():
    data = diagnosis_to_dict(
        diagnosis(
            '/qos_demo/durability',
            [endpoint('volatile_publisher', durability='volatile')],
            [endpoint('transient_local_subscriber', durability='transient_local')],
        ),
        mode='single_topic',
    )

    parsed = parse_json(data)

    assert parsed['compatible'] is False
    assert parsed['issues'][0]['policy'] == 'durability'
    assert parsed['issues'][0]['publisher_value'] == 'volatile'
    assert parsed['issues'][0]['subscriber_value'] == 'transient_local'


def test_single_topic_json_compatible_topic_has_no_issues():
    data = diagnosis_to_dict(
        diagnosis(
            '/qos_demo/reliability_compatible',
            [endpoint('reliable_publisher', reliability='reliable')],
            [endpoint('best_effort_subscriber', reliability='best_effort')],
        ),
        mode='single_topic',
    )

    parsed = parse_json(data)

    assert parsed['compatible'] is True
    assert parsed['issues'] == []
    assert parsed['publishers'][0]['qos']['reliability'] == 'reliable'
    assert parsed['subscribers'][0]['qos']['reliability'] == 'best_effort'


def test_all_topics_json_filters_compatible_topics_by_default():
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

    parsed = parse_json(
        system_scan_to_dict(build_system_scan_result([incompatible, compatible]))
    )

    assert parsed['mode'] == 'all_topics'
    assert parsed['summary']['scanned_topics'] == 2
    assert parsed['summary']['topics_with_qos_issues'] == 1
    assert parsed['summary']['reported_topics'] == 1
    assert [topic['topic'] for topic in parsed['topics']] == ['/qos_demo/reliability']


def test_all_topics_json_no_issues_reports_empty_topics_by_default():
    compatible = diagnosis(
        '/qos_demo/reliability_compatible',
        [endpoint('reliable_publisher')],
        [endpoint('best_effort_subscriber', reliability='best_effort')],
    )

    parsed = parse_json(system_scan_to_dict(build_system_scan_result([compatible])))

    assert parsed['summary']['topics_with_qos_issues'] == 0
    assert parsed['summary']['reported_topics'] == 0
    assert parsed['topics'] == []


def test_all_topics_json_show_compatible_includes_compatible_topics():
    compatible = diagnosis(
        '/qos_demo/reliability_compatible',
        [endpoint('reliable_publisher')],
        [endpoint('best_effort_subscriber', reliability='best_effort')],
    )

    parsed = parse_json(
        system_scan_to_dict(
            build_system_scan_result([compatible]),
            show_compatible=True,
        )
    )

    assert parsed['summary']['reported_topics'] == 1
    assert parsed['topics'][0]['topic'] == '/qos_demo/reliability_compatible'
    assert parsed['topics'][0]['compatible'] is True


def test_json_unknown_values_are_null_and_no_terminal_icons_are_present():
    data = diagnosis_to_dict(
        diagnosis(
            '/unknown',
            [EndpointQoS(node_name='talker')],
            [],
        ),
        mode='single_topic',
    )
    output = format_json(data)
    parsed = json.loads(output)

    assert parsed['publishers'][0]['qos']['reliability'] is None
    assert '❌' not in output
    assert '✅' not in output
    assert '\x1b[' not in output
