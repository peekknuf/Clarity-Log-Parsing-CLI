import pytest
from datetime import datetime, timedelta
from src.utils.utils import (
    timestamp_to_datetime,
    is_within_last_hour,
    is_in_timerange,
    parse_datetime_input
)

def test_timestamp_to_datetime():
    """Test conversion of timestamp to datetime."""
    # Test current time
    now = datetime.now()
    timestamp = int(now.timestamp())
    converted = timestamp_to_datetime(timestamp)
    assert abs((converted - now).total_seconds()) < 1  # Allow 1 second difference

    # Test specific timestamp (using UTC to avoid timezone issues)
    timestamp = 1704067200  # 2024-01-01 00:00:00 UTC
    converted = timestamp_to_datetime(timestamp)
    assert converted.year == 2024
    assert converted.month == 1
    assert converted.day == 1
    # Don't test hours as they may vary by timezone
    assert converted.minute == 0
    assert converted.second == 0

def test_is_within_last_hour():
    """Test checking if timestamp is within the last hour."""
    now = datetime.now()

    # Test timestamp from 30 minutes ago
    timestamp = int((now - timedelta(minutes=30)).timestamp())
    assert is_within_last_hour(timestamp) is True

    # Test timestamp from 2 hours ago
    timestamp = int((now - timedelta(hours=2)).timestamp())
    assert is_within_last_hour(timestamp) is False

    # Test timestamp from exactly 1 hour ago (minus 1 second to ensure it's within)
    timestamp = int((now - timedelta(hours=1) + timedelta(seconds=1)).timestamp())
    assert is_within_last_hour(timestamp) is True

    # Test future timestamp
    future_timestamp = int((now + timedelta(minutes=30)).timestamp())
    assert is_within_last_hour(future_timestamp) is True

def test_is_in_timerange():
    """Test checking if timestamp is within a specified time range."""
    now = datetime.now()
    start_time = now - timedelta(hours=1)
    end_time = now + timedelta(hours=1)

    # Test timestamp within range
    timestamp = int(now.timestamp())
    assert is_in_timerange(timestamp, start_time, end_time) is True

    # Test timestamp before range
    before_timestamp = int((start_time - timedelta(minutes=1)).timestamp())
    assert is_in_timerange(before_timestamp, start_time, end_time) is False

    # Test timestamp after range
    after_timestamp = int((end_time + timedelta(minutes=1)).timestamp())
    assert is_in_timerange(after_timestamp, start_time, end_time) is False

    # Test with only start_time
    assert is_in_timerange(timestamp, start_time) is True
    assert is_in_timerange(before_timestamp, start_time) is False

    # Test with only end_time
    assert is_in_timerange(timestamp, end_time=end_time) is True
    assert is_in_timerange(after_timestamp, end_time=end_time) is False

    # Test with no time bounds
    assert is_in_timerange(timestamp) is True

def test_parse_datetime_input():
    """Test parsing datetime input strings."""
    # Test valid format
    dt_str = "2024-01-01 12:34:56"
    expected = datetime(2024, 1, 1, 12, 34, 56)
    assert parse_datetime_input(dt_str) == expected

    # Test invalid format
    with pytest.raises(ValueError) as exc_info:
        parse_datetime_input("2024/01/01 12:34:56")
    assert "Invalid datetime format" in str(exc_info.value)

    # Test empty input
    assert parse_datetime_input("") is None
    assert parse_datetime_input(None) is None

    # Test invalid values
    with pytest.raises(ValueError):
        parse_datetime_input("2024-13-01 12:34:56")  # Invalid month

    with pytest.raises(ValueError):
        parse_datetime_input("2024-01-32 12:34:56")  # Invalid day

    with pytest.raises(ValueError):
        parse_datetime_input("2024-01-01 25:34:56")  # Invalid hour