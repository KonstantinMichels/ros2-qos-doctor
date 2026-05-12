import pytest

from ros2_qos_doctor.qos_doctor import build_parser


def test_parser_rejects_negative_timeout():
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(['/chatter', '--timeout', '-1'])
