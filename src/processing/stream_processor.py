import os
import time
import logging
from datetime import datetime, timedelta
from typing import Set, Dict, TypedDict, Optional
from pathlib import Path

from src.parser.parser import parse_log_line
from src.utils.utils import is_within_last_hour

logger = logging.getLogger(__name__)

FileTracker = TypedDict(
    "FileTracker",
    {"file_path": str, "last_position": int, "last_modified": Optional[float]},
)


def create_file_tracker(file_path: str) -> FileTracker:
    """Create a tracker dictionary for a log file."""
    try:
        last_modified = os.path.getmtime(file_path)
        return {
            "file_path": file_path,
            "last_position": 0,
            "last_modified": last_modified,
        }
    except FileNotFoundError:
        return {
            "file_path": file_path,
            "last_position": 0,
            "last_modified": None,
        }


def process_stream(
    log_dir: str,
    target_host: str,
    from_host: Optional[str] = None,
    max_iterations: Optional[int] = None,
) -> None:
    """
    Monitor a directory for log files and report connection statistics every 10 seconds.

    Args:
        log_dir: Directory containing log files to monitor
        target_host: Host to track connections to
        from_host: Optional host to track connections from
        max_iterations: Optional maximum number of monitoring iterations (for testing)
    """
    log_dir_path = Path(log_dir)
    tracked_files: Dict[str, FileTracker] = {}
    connections_to = set()
    connections_from = set()
    connection_counts = {}
    last_report_time = datetime.now()
    last_dir_check = datetime.now()
    iteration_count = 0

    logger.info(f"Starting real-time monitoring of directory: {log_dir}")
    logger.info(f"Tracking connections to {target_host}")
    if from_host:
        logger.info(f"Tracking connections from {from_host}")
    logger.info("Press Ctrl+C to stop monitoring")

    try:
        while True:
            iteration_count += 1
            if max_iterations and iteration_count > max_iterations:
                break

            now = datetime.now()

            if now - last_dir_check >= timedelta(seconds=1):
                for file_path in log_dir_path.glob("*.log"):
                    str_path = str(file_path)
                    if str_path not in tracked_files:
                        logger.info(f"Found new log file: {file_path}")
                        tracked_files[str_path] = create_file_tracker(str_path)
                last_dir_check = now

            for file_path, tracker in list(tracked_files.items()):
                try:
                    current_size = os.path.getsize(file_path)
                    current_modified = os.path.getmtime(file_path)

                    if (
                        current_modified == tracker["last_modified"]
                        and current_size <= tracker["last_position"]
                    ):
                        continue

                    if current_size < tracker["last_position"]:
                        logger.info(
                            f"Log file {file_path} appears to have been truncated, resetting position"
                        )
                        tracker["last_position"] = 0

                    with open(file_path, "r") as f:
                        f.seek(tracker["last_position"])
                        for line in f:
                            parsed = parse_log_line(line)
                            if not parsed:
                                continue

                            timestamp, source, destination = parsed

                            if not is_within_last_hour(timestamp):
                                continue

                            if destination == target_host:
                                connections_to.add(source)

                            if source == target_host or (
                                from_host and source == from_host
                            ):
                                connections_from.add(destination)

                            connection_counts[source] = (
                                connection_counts.get(source, 0) + 1
                            )

                        tracker["last_position"] = f.tell()
                        tracker["last_modified"] = current_modified

                except FileNotFoundError:
                    logger.info(f"Log file {file_path} was removed, stopping tracking")
                    del tracked_files[file_path]
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")

            if now - last_report_time >= timedelta(seconds=10):
                generate_report(
                    target_host, connections_to, connections_from, connection_counts
                )
                last_report_time = now

                connections_to = set()
                connections_from = set()
                connection_counts = {}

            time.sleep(0.1)

    finally:
        if connections_to or connections_from or connection_counts:
            logger.info("Generating final report")
            generate_report(
                target_host, connections_to, connections_from, connection_counts
            )


def generate_report(
    target_host: str,
    connections_to: Set[str],
    connections_from: Set[str],
    connection_counts: Dict[str, int],
) -> None:
    """Generate and print the report every 10 seconds."""
    print("\n" + "=" * 50)
    print(f"REPORT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    print(f"\nHosts connected TO {target_host} in the last 10 seconds:")
    if connections_to:
        for host in sorted(connections_to):
            print(f"  - {host}")
    else:
        print("  None")

    print(
        f"\nHosts that received connections FROM {target_host} in the last 10 seconds:"
    )
    if connections_from:
        for host in sorted(connections_from):
            print(f"  - {host}")
    else:
        print("  None")

    if connection_counts:
        most_active_host, count = max(connection_counts.items(), key=lambda x: x[1])
        print(
            f"\nMost active host in the last 10 seconds: {most_active_host} ({count} connections)"
        )
    else:
        print("\nNo connections recorded in the last 10 seconds")

    print("=" * 50)
