import os
import time
import logging
from datetime import datetime, timedelta
from typing import Set, Dict, Optional, Tuple

from src.parser.parser import parse_log_line


logger = logging.getLogger(__name__)


class StreamProcessor:
    def __init__(
        self, log_file: str, target_host: str, from_host: Optional[str] = None
    ):
        self.log_file = log_file
        self.target_host = target_host
        self.from_host = from_host
        self.last_position = 0
        self.connections_to = set()
        self.connections_from = set()
        self.connection_counts = {}
        self.last_report_time = datetime.now()

    def process_new_lines(self) -> None:
        """Process new lines added to the log file since last check."""
        if not os.path.exists(self.log_file):
            logger.warning(
                f"Log file {self.log_file} does not exist yet, waiting..."
            )
            return

        current_size = os.path.getsize(self.log_file)

        # If file is smaller than last position (truncated or rotated)
        if current_size < self.last_position:
            logger.info(
                "Log file appears to have been truncated, resetting position"
            )
            self.last_position = 0

        if current_size <= self.last_position:
            return  

        with open(self.log_file, "r") as f:
            f.seek(self.last_position)
            for line in f:
                self._process_line(line)

            self.last_position = f.tell()

    def _process_line(self, line: str) -> None:
        """Process a single log line, updating connection tracking."""
        parsed = parse_log_line(line)
        if not parsed:
            return

        timestamp, source, destination = parsed

        # Check if within the last hour
        log_time = datetime.fromtimestamp(timestamp)
        if datetime.now() - log_time > timedelta(hours=1):
            return

        # Track connections to target host
        if destination == self.target_host:
            self.connections_to.add(source)

        # Track connections from target host or specified from_host
        if source == self.target_host or (
            self.from_host and source == self.from_host
        ):
            self.connections_from.add(destination)

        # Count connections by source
        self.connection_counts[source] = (
            self.connection_counts.get(source, 0) + 1
        )

    def should_report(self) -> bool:
        """Check if it's time to generate an hourly report."""
        now = datetime.now()
        if now - self.last_report_time >= timedelta(hours=1):
            self.last_report_time = now
            return True
        return False

    def generate_report(self) -> None:
        """Generate and print the hourly report."""
        print("\n" + "=" * 50)
        print(f"HOURLY REPORT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)

        print(f"\nHosts connected TO {self.target_host} in the last hour:")
        if self.connections_to:
            for host in sorted(self.connections_to):
                print(f"  - {host}")
        else:
            print("  None")

        # Hosts that received connections from target.
        print(
            f"\nHosts that received connections FROM {self.target_host} in the last hour:"
        )
        if self.connections_from:
            for host in sorted(self.connections_from):
                print(f"  - {host}")
        else:
            print("  None")

        # Most active host
        if self.connection_counts:
            most_active_host, count = max(
                self.connection_counts.items(), key=lambda x: x[1]
            )
            print(
                f"\nMost active host: {most_active_host} ({count} connections)"
            )
        else:
            print("\nNo connections recorded in the last hour")

        print("=" * 50)

        # Reset tracking for next hour
        self.connections_to = set()
        self.connections_from = set()
        self.connection_counts = {}


def process_stream(
    log_file: str, target_host: str, from_host: Optional[str] = None
) -> None:
    """
    Monitor a log file in real-time and report connection statistics hourly.

    Args:
        log_file: Path to the log file to monitor
        target_host: Host to track connections to
        from_host: Optional host to track connections from
    """
    processor = StreamProcessor(log_file, target_host, from_host)

    logger.info(f"Starting real-time monitoring of {log_file}")
    logger.info(f"Tracking connections to {target_host}")
    if from_host:
        logger.info(f"Tracking connections from {from_host}")
    logger.info("Press Ctrl+C to stop monitoring")

    try:
        while True:
            processor.process_new_lines()

            if processor.should_report():
                processor.generate_report()

            # Sleep to reduce CPU usage
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
