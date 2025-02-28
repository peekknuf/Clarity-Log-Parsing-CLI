from datetime import datetime
from typing import Set, Optional

from src.parser.parser import find_connected_hosts


def process_batch(
    log_file: str,
    hostname: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> Set[str]:
    """
    Process a log file to find hosts connected to the given hostname
    within the specified time range.

    Args:
        log_file: Path to the log file
        hostname: Host to analyze connections to
        start_time: Optional start of time range
        end_time: Optional end of time range

    Returns:
        Set of hostnames that connected to the specified host
    """
    return find_connected_hosts(log_file, hostname, start_time, end_time)
