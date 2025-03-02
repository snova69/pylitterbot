"""Test utils module."""

from pylitterbot.utils import (
    REDACTED,
    decode,
    encode,
    first_value,
    redact,
    round_time,
    to_timestamp,
)


def test_round_time_default() -> None:
    """Tests rouding a timestamp."""
    timestamp = round_time()
    assert timestamp


def test_to_timestamp() -> None:
    """Tests parsing a Litter-Robot timestamp."""
    assert to_timestamp(None) is None
    assert to_timestamp("2022-09-14") is not None


def test_encode_decode() -> None:
    """Test encoding and decoding of values."""
    value = "test"
    assert (encoded := encode(value)) == "dGVzdA=="
    assert decode(encoded) == value
    assert encode({value: value}) == "eyJ0ZXN0IjogInRlc3QifQ=="


def test_redact() -> None:
    """Test redacting values from a dictionary."""
    assert redact({"litterRobotId": None}) == {"litterRobotId": None}
    assert redact({"litterRobotId": "someId"}) == {"litterRobotId": REDACTED}

    data = {"key": "value"}
    assert redact(data) == data
    assert redact([data, data]) == [data, data]


def test_first_value() -> None:
    """Test looking up values from a dictionary."""
    values = {"key1": 1, "key2": 2, "key4": 4}
    assert first_value(values, ("key1", "key2")) == 1
    assert first_value(values, ("key2", "key3")) == 2
    assert first_value(values, ("key3", "key4")) == 4
    assert first_value(values, ("key3", "key5")) is None
    assert first_value(values, ("key3", "key5"), 0) == 0
    assert first_value(None, ("key3", "key5"), 10) == 10
