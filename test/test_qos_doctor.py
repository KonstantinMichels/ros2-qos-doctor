import pytest

from ros2_qos_doctor.qos_doctor import build_parser, get_topic_types, validate_args


def test_parser_rejects_negative_timeout():
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(['/chatter', '--timeout', '-1'])


def test_parser_accepts_single_topic_mode():
    parser = build_parser()
    args = parser.parse_args(['/chatter'])

    validate_args(parser, args)

    assert args.topic_name == '/chatter'
    assert not args.scan_all


def test_parser_accepts_all_topics_mode():
    parser = build_parser()
    args = parser.parse_args(['--all', '--show-compatible', '--rosbag2-yaml'])

    validate_args(parser, args)

    assert args.topic_name is None
    assert args.scan_all
    assert args.show_compatible
    assert args.rosbag2_yaml


def test_parser_rejects_missing_topic_and_missing_all():
    parser = build_parser()
    args = parser.parse_args([])

    with pytest.raises(SystemExit):
        validate_args(parser, args)


def test_parser_rejects_topic_with_all():
    parser = build_parser()
    args = parser.parse_args(['/chatter', '--all'])

    with pytest.raises(SystemExit):
        validate_args(parser, args)


def test_parser_rejects_show_compatible_without_all():
    parser = build_parser()
    args = parser.parse_args(['/chatter', '--show-compatible'])

    with pytest.raises(SystemExit):
        validate_args(parser, args)


class FakeTopicNode:
    def get_topic_names_and_types(self):
        return [
            ('/chatter', ['std_msgs/msg/String']),
            ('/image', ['sensor_msgs/msg/Image']),
        ]


def test_get_topic_types_returns_types_for_single_topic_json():
    assert get_topic_types(FakeTopicNode(), '/chatter') == ['std_msgs/msg/String']
    assert get_topic_types(FakeTopicNode(), '/missing') == []
