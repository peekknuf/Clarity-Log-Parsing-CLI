import pytest
import tempfile
import os
from datetime import datetime, timedelta

from src.parser.parser import (
    parse_log_line,
    filter_by_timerange,
    find_connected_hosts,
    find_hosts_connected_to,
    count_connections_by_host,
    find_most_active_host,
)


@pytest.fixture
def sample_log_file():
    test_log = tempfile.NamedTemporaryFile(delete=False)

    now = int(datetime.now().timestamp())
    hour_ago = int((datetime.now() - timedelta(hours=1)).timestamp())

    log_data = [
        f"{hour_ago} host1 host2\n",
        f"{hour_ago + 60} host3 host1\n",
        f"{hour_ago + 120} host2 host3\n",
        f"{hour_ago + 180} host1 host3\n",
        f"{now - 300} host3 host2\n",
        f"{now - 240} host1 host4\n",
        f"{now - 180} host4 host1\n",
        f"{now - 120} host2 host1\n",
        f"{now - 60} host3 host1\n",
    ]

    test_log.writelines(line.encode() for line in log_data)
    test_log.flush()

    time_refs = {
        "start_time": datetime.fromtimestamp(hour_ago),
        "mid_time": datetime.fromtimestamp(hour_ago + 300),
        "end_time": datetime.now(),
    }

    yield test_log.name, time_refs

    test_log.close()
    os.unlink(test_log.name)


@pytest.fixture
def real_log_file():
    test_log = tempfile.NamedTemporaryFile(delete=False)

    log_data = [
        "1704068314 host22 host29\n",
        "1704072476 host74 host35\n",
        "1704073616 host33 host43\n",
        "1704075119 host92 host88\n",
        "1704076025 host2 host80\n",
        "1704080440 host4 host82\n",
        "1704085178 host35 host20\n",
        "1704086472 host20 host92\n",
        "1704087120 host58 host94\n",
        "1704089933 host14 host80\n",
        "1704092086 host78 host77\n",
        "1704096639 host6 host78\n",
        "1704097073 host99 host58\n",
        "1704097111 host66 host91\n",
        "1704097950 host76 host23\n",
        "1704097970 host31 host27\n",
        "1704104842 host40 host1\n",
        "1704110516 host75 host49\n",
        "1704114735 host11 host29\n",
        "1704118874 host91 host25\n",
        "1704122732 host1 host11\n",
    ]

    test_log.writelines(line.encode() for line in log_data)
    test_log.flush()

    yield test_log.name

    # Cleanup
    test_log.close()
    os.unlink(test_log.name)


def test_parse_log_line():
    result = parse_log_line("1366815793 quark garak")
    assert result == (1366815793, "quark", "garak")

    assert parse_log_line("") is None
    assert parse_log_line("invalid line") is None
    assert parse_log_line("1366815793 quark") is None
    assert parse_log_line("quark garak") is None


def test_filter_by_timerange(sample_log_file):
    log_path, time_refs = sample_log_file

    results = list(filter_by_timerange(log_path))
    assert len(results) == 9

    results = list(filter_by_timerange(log_path, start_time=time_refs["mid_time"]))
    assert all(ts >= int(time_refs["mid_time"].timestamp()) for ts, _, _ in results)

    results = list(filter_by_timerange(log_path, end_time=time_refs["mid_time"]))
    assert all(ts <= int(time_refs["mid_time"].timestamp()) for ts, _, _ in results)

    results = list(
        filter_by_timerange(
            log_path,
            start_time=time_refs["start_time"],
            end_time=time_refs["mid_time"],
        )
    )
    assert all(
        int(time_refs["start_time"].timestamp())
        <= ts
        <= int(time_refs["mid_time"].timestamp())
        for ts, _, _ in results
    )


def test_find_connected_hosts(sample_log_file):
    log_path, time_refs = sample_log_file

    # Find hosts connected to host1
    connected = find_connected_hosts(log_path, "host1")
    assert connected == {"host3", "host4", "host2"}

    # With time range
    connected = find_connected_hosts(
        log_path, "host1", start_time=time_refs["mid_time"]
    )
    assert connected == {"host4", "host2", "host3"}


def test_find_hosts_connected_to(sample_log_file):
    log_path, time_refs = sample_log_file

    # Find hosts that host1 connected to
    connected_to = find_hosts_connected_to(log_path, "host1")
    assert connected_to == {"host2", "host3", "host4"}


def test_count_connections_by_host(sample_log_file):
    log_path, time_refs = sample_log_file

    counts = count_connections_by_host(log_path)
    assert counts["host1"] == 3
    assert counts["host2"] == 2
    assert counts["host3"] == 3
    assert counts["host4"] == 1


def test_find_most_active_host(sample_log_file):
    log_path, time_refs = sample_log_file
    host, count = find_most_active_host(log_path)
    assert host in ["host1", "host3"]
    assert count == 3


def test_parse_real_log_line(real_log_file):
    result = parse_log_line("1704068314 host22 host29")
    assert result == (1704068314, "host22", "host29")


def test_filter_by_real_timerange(real_log_file):
    # Test time filtering with real data
    start_time = datetime.fromtimestamp(1704080000)  # Around Jan 1, 2024
    end_time = datetime.fromtimestamp(1704090000)  # A bit later

    results = list(
        filter_by_timerange(real_log_file, start_time=start_time, end_time=end_time)
    )

    # Should include entries between the timestamps
    assert len(results) > 0
    assert all(1704080000 <= ts <= 1704090000 for ts, _, _ in results)


def test_connected_hosts_real_data(real_log_file):
    # Test finding hosts connected to host80
    connected = find_connected_hosts(real_log_file, "host80")
    assert "host2" in connected
    assert "host14" in connected

    # Test finding hosts connected to host29
    connected = find_connected_hosts(real_log_file, "host29")
    assert "host22" in connected
    assert "host11" in connected

    # Test with time filtering
    start_time = datetime.fromtimestamp(1704110000)
    connected = find_connected_hosts(real_log_file, "host29", start_time=start_time)
    assert "host11" in connected
    assert "host22" not in connected  # This is before our start time


def test_parse_log_line_edge_cases():
    """Test parse_log_line with various edge cases."""
    # Test empty line
    assert parse_log_line("") is None

    # Test whitespace only
    assert parse_log_line("   ") is None

    # Test invalid formats
    assert parse_log_line("invalid") is None
    assert parse_log_line("123") is None
    assert parse_log_line("123 host1") is None
    assert parse_log_line("host1 host2") is None
    assert parse_log_line("abc host1 host2") is None

    # Test with extra whitespace
    assert parse_log_line("  1366815793   quark    garak  ") == (
        1366815793,
        "quark",
        "garak",
    )

    # Test with very large timestamp
    assert parse_log_line("9999999999 host1 host2") == (9999999999, "host1", "host2")

    # Test with special characters in hostnames
    assert parse_log_line("1366815793 host-1.domain host-2.domain") == (
        1366815793,
        "host-1.domain",
        "host-2.domain",
    )


def test_find_connected_hosts_edge_cases(sample_log_file):
    """Test find_connected_hosts with edge cases."""
    log_path, time_refs = sample_log_file

    # Test with non-existent host
    assert find_connected_hosts(log_path, "non_existent_host") == set()

    # Test with empty time range
    start_time = end_time = datetime.fromtimestamp(time_refs["start_time"].timestamp())
    assert find_connected_hosts(log_path, "host1", start_time, end_time) == set()

    # Test with reversed time range
    with pytest.raises(ValueError):
        find_connected_hosts(
            log_path, "host1", time_refs["end_time"], time_refs["start_time"]
        )


def test_find_hosts_connected_to_comprehensive(sample_log_file):
    """Test find_hosts_connected_to with comprehensive scenarios."""
    log_path, time_refs = sample_log_file

    connected_to = find_hosts_connected_to(log_path, "host1")
    assert "host2" in connected_to
    assert "host3" in connected_to
    assert "host4" in connected_to

    recent_connections = find_hosts_connected_to(
        log_path, "host1", start_time=time_refs["mid_time"]
    )
    assert "host4" in recent_connections
    assert "host2" not in recent_connections

    assert find_hosts_connected_to(log_path, "non_existent") == set()


def test_count_connections_comprehensive(sample_log_file):
    """Test connection counting with various scenarios."""
    log_path, time_refs = sample_log_file

    # Test total counts
    counts = count_connections_by_host(log_path)
    assert counts["host1"] >= 2  # host1 makes at least 2 connections
    assert counts["host2"] >= 1  # host2 makes at least 1 connection

    # Test counts within time range
    recent_counts = count_connections_by_host(
        log_path, start_time=time_refs["mid_time"]
    )
    assert (
        recent_counts["host1"] < counts["host1"]
    )  # Should have fewer recent connections

    # Test with empty time range
    empty_counts = count_connections_by_host(
        log_path, start_time=datetime.now(), end_time=datetime.now()
    )
    assert empty_counts == {}


def test_find_most_active_host_comprehensive(sample_log_file):
    """Test finding most active host with various scenarios."""
    log_path, time_refs = sample_log_file

    most_active, count = find_most_active_host(log_path)
    assert most_active in ["host1", "host2", "host3"]
    assert count > 0

    recent_active, recent_count = find_most_active_host(
        log_path, start_time=time_refs["mid_time"]
    )
    assert recent_count <= count

    empty_active, empty_count = find_most_active_host(
        log_path, start_time=datetime.now(), end_time=datetime.now()
    )
    assert empty_active == ""
    assert empty_count == 0


def test_filter_by_timerange_edge_cases(sample_log_file):
    """Test filter_by_timerange with edge cases."""
    log_path, time_refs = sample_log_file

    # Test with equal start and end time
    timestamp = time_refs["mid_time"]
    results = list(filter_by_timerange(log_path, timestamp, timestamp))
    assert len(results) == 0  # Should be empty as it's an instant in time

    # Test with reversed time range
    with pytest.raises(ValueError):
        list(
            filter_by_timerange(
                log_path, time_refs["end_time"], time_refs["start_time"]
            )
        )

    # Test with future time range
    future_time = datetime.now() + timedelta(days=1)
    results = list(filter_by_timerange(log_path, future_time))
    assert len(results) == 0  # Should be empty as it's in the future
