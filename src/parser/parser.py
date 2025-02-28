import re
from datetime import datetime
from typing import Dict, Set, Tuple, Iterator, Optional

LOG_PATTERN = re.compile(r"^(\d+)\s+(\S+)\s+(\S+)$")


def parse_log_line(line: str) -> Optional[Tuple[int, str, str]]:
    """
    Parse a single log line into (timestamp, source_host, dest_host).
    Returns None if the line doesn't match expected format.
    """
    match = LOG_PATTERN.match(line.strip())
    if not match:
        return None

    timestamp, source, destination = match.groups()
    return int(timestamp), source, destination


def filter_by_timerange(
    log_file: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> Iterator[Tuple[int, str, str]]:
    """
    Generator that yields log entries filtered by time range.
    Handles files that may be partially time-sorted (within 5 minutes).
    """
    start_timestamp = int(start_time.timestamp()) if start_time else 0
    end_timestamp = int(end_time.timestamp()) if end_time else float("inf")

    with open(log_file, "r") as f:
        for line in f:
            parsed = parse_log_line(line)
            if not parsed:
                continue

            timestamp, source, destination = parsed
            if start_timestamp <= timestamp <= end_timestamp:
                yield timestamp, source, destination


def find_connected_hosts(
    log_file: str,
    hostname: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> Set[str]:
    """
    Find all hosts that connected to the specified hostname within the time range.
    """
    connected_hosts = set()

    for timestamp, source, destination in filter_by_timerange(
        log_file, start_time, end_time
    ):
        if destination == hostname:
            connected_hosts.add(source)

    return connected_hosts


def find_hosts_connected_to(
    log_file: str,
    hostname: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> Set[str]:
    """
    Find all hosts that the specified hostname connected to within the time range.
    """
    hosts_connected_to = set()

    for timestamp, source, destination in filter_by_timerange(
        log_file, start_time, end_time
    ):
        if source == hostname:
            hosts_connected_to.add(destination)

    return hosts_connected_to


def count_connections_by_host(
    log_file: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> Dict[str, int]:
    """
    Count outgoing connections made by each host within the time range.
    Returns a dictionary mapping hostnames to connection counts.
    """
    connection_counts = {}

    for timestamp, source, destination in filter_by_timerange(
        log_file, start_time, end_time
    ):
        connection_counts[source] = connection_counts.get(source, 0) + 1

    return connection_counts


def find_most_active_host(
    log_file: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> Tuple[str, int]:
    """
    Find the host that generated the most connections within the time range.
    Returns tuple of (hostname, connection_count).
    """
    connection_counts = count_connections_by_host(
        log_file, start_time, end_time
    )

    if not connection_counts:
        return None, 0

    return max(connection_counts.items(), key=lambda x: x[1])
