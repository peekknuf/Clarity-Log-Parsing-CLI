import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def get_file_size(file_path: str) -> int:
    """Get the size of a file in bytes, safely handling non-existent files."""
    try:
        return os.path.getsize(file_path)
    except (FileNotFoundError, OSError):
        return 0

def timestamp_to_datetime(timestamp: int) -> datetime:
    """Convert a Unix timestamp to a datetime object."""
    return datetime.fromtimestamp(timestamp)

def is_within_last_hour(timestamp: int) -> bool:
    """Check if a timestamp is within the last hour."""
    dt = timestamp_to_datetime(timestamp)
    return datetime.now() - dt <= timedelta(hours=1)

def is_in_timerange(timestamp: int, start_time=None, end_time=None) -> bool:
    """Check if a timestamp is within the specified time range."""
    if start_time and timestamp < start_time.timestamp():
        return False
    if end_time and timestamp > end_time.timestamp():
        return False
    return True
