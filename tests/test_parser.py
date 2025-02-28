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

    results = list(
        filter_by_timerange(log_path, start_time=time_refs["mid_time"])
    )
    assert all(
        ts >= int(time_refs["mid_time"].timestamp()) for ts, _, _ in results
    )

    results = list(
        filter_by_timerange(log_path, end_time=time_refs["mid_time"])
    )
    assert all(
        ts <= int(time_refs["mid_time"].timestamp()) for ts, _, _ in results
    )

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

    # Both host1 and host3 have 3 connections, should return the one with highest count
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
        filter_by_timerange(
            real_log_file, start_time=start_time, end_time=end_time
        )
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
    connected = find_connected_hosts(
        real_log_file, "host29", start_time=start_time
    )
    assert "host11" in connected
    assert "host22" not in connected  # This is before our start time
