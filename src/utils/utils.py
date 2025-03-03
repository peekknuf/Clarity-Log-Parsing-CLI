import os
import logging
from datetime import datetime, timedelta


def get_file_size(file_path: str) -> int:
    try:
        return os.path.getsize(file_path)
    except (FileNotFoundError, OSError):
        return 0

def timestamp_to_datetime(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp)

def is_within_last_hour(timestamp: int) -> bool:
    dt = timestamp_to_datetime(timestamp)
    return datetime.now() - dt <= timedelta(hours=1)

def is_in_timerange(timestamp: int, start_time=None, end_time=None) -> bool:
    if start_time and timestamp < start_time.timestamp():
        return False
    if end_time and timestamp > end_time.timestamp():
        return False
    return True

def parse_datetime_input(dt_str: str) -> datetime:
    if not dt_str:
        return None
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        raise ValueError(f"Invalid datetime format. Use YYYY-MM-DD HH:MM:SS format") from e
