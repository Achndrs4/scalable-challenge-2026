import json
from validate import _validate_chunk


def test_valid_lines_pass():
    lines = ['{"user_name": "u1", "listened_at": 1}', '{"user_name": "u2", "listened_at": 2}']
    valid, rejected = _validate_chunk(lines)
    assert len(valid) == 2
    assert rejected == 0


def test_malformed_json_rejected():
    lines = ["not json", '{"broken":}', "   ", ""]
    valid, rejected = _validate_chunk(lines)
    assert valid == []
    assert rejected == 4


def test_json_array_rejected():
    lines = ["[1, 2, 3]", '["a", "b"]']
    valid, rejected = _validate_chunk(lines)
    assert valid == []
    assert rejected == 2


def test_mixed_chunk():
    lines = [
        '{"user_name": "u1", "listened_at": 1}',
        "not json",
        '{"user_name": "u2", "listened_at": 2}',
        "[1, 2, 3]",
        "",
    ]
    valid, rejected = _validate_chunk(lines)
    assert len(valid) == 2
    assert rejected == 3


def test_validate_task_filters_mixed_file(mixed_jsonl):
    from validate import validate
    clean_path = validate.fn(mixed_jsonl)
    with open(clean_path) as f:
        lines = [l for l in f.readlines() if l.strip()]
    assert len(lines) == 2
    for line in lines:
        assert isinstance(json.loads(line), dict)
