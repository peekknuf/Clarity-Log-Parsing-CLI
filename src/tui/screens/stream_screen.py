"""Stream screen for monitoring log files in real-time."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static, Log
from textual.screen import Screen
from textual.worker import get_current_worker
from datetime import datetime, timedelta
from pathlib import Path
import os
import time

from src.processing.stream_processor import create_file_tracker, parse_log_line
from src.utils.utils import is_within_last_hour

class StreamScreen(Screen):
    """Screen for monitoring log files in real-time."""

    BINDINGS = [("ctrl+c", "quit", "Quit")]

    def __init__(self, directory: str, host: str):
        super().__init__()
        self.directory = directory
        self.host = host
        self.log_widget = None
        self.tracked_files = {}
        self.connections_to = set()
        self.connections_from = set()
        self.connection_counts = {}
        self.last_report_time = datetime.now()
        self.last_dir_check = datetime.now()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static(f"Monitoring connections for {self.host}", classes="stream-header"),
            Log(highlight=True, id="stream-log"),
            classes="stream-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        self.log_widget = self.query_one("#stream-log")
        self.start_monitoring()

    def start_monitoring(self) -> None:
        self.run_worker(self.monitor_directory, thread=True)

    def write_log(self, text: str, style: str = "") -> None:
        """Write to log."""
        self.log_widget.write(text)

    def monitor_directory(self) -> None:
        worker = get_current_worker()
        log_dir_path = Path(self.directory)
        self.write_log("Starting monitoring...\n")

        while not worker.is_cancelled:
            now = datetime.now()

            # Check for new files
            if now - self.last_dir_check >= timedelta(seconds=1):
                for file_path in log_dir_path.glob("*.log"):
                    str_path = str(file_path)
                    if str_path not in self.tracked_files:
                        self.write_log(f"Found new log file: {file_path}\n")
                        self.tracked_files[str_path] = create_file_tracker(str_path)
                self.last_dir_check = now

            # Process files
            for file_path, tracker in list(self.tracked_files.items()):
                try:
                    current_size = os.path.getsize(file_path)
                    current_modified = os.path.getmtime(file_path)

                    # Reset position if file was truncated
                    if current_size < tracker["last_position"]:
                        self.write_log(f"Log file {file_path} was truncated, resetting position\n")
                        tracker["last_position"] = 0

                    # Check for new content
                    if current_size > tracker["last_position"] or current_modified > tracker["last_modified"]:
                        with open(file_path, 'r') as f:
                            f.seek(tracker["last_position"])
                            for line in f:
                                parsed = parse_log_line(line)
                                if not parsed:
                                    continue

                                timestamp, source, destination = parsed

                                if not is_within_last_hour(timestamp):
                                    continue

                                if destination == self.host:
                                    self.connections_to.add(source)

                                if source == self.host:
                                    self.connections_from.add(destination)

                                self.connection_counts[source] = self.connection_counts.get(source, 0) + 1

                            tracker["last_position"] = f.tell()
                            tracker["last_modified"] = current_modified

                except FileNotFoundError:
                    self.write_log(f"Log file {file_path} was removed\n")
                    del self.tracked_files[file_path]
                except Exception as e:
                    self.write_log(f"Error processing {file_path}: {e}\n")

            # Generate report every 10 seconds
            if now - self.last_report_time >= timedelta(seconds=10):
                self.generate_tui_report()
                self.last_report_time = now
                self.connections_to = set()
                self.connections_from = set()
                self.connection_counts = {}

            time.sleep(0.1)

    def generate_tui_report(self) -> None:
        separator = "=" * 50 + "\n"
        self.write_log(separator)
        self.write_log(f"REPORT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.write_log(separator)

        self.write_log(f"Hosts connected TO {self.host} in the last 10 seconds:\n")
        if self.connections_to:
            for host in sorted(self.connections_to):
                self.write_log(f"  • {host}\n")
        else:
            self.write_log("  None\n")

        self.write_log(f"\nHosts that received connections FROM {self.host} in the last 10 seconds:\n")
        if self.connections_from:
            for host in sorted(self.connections_from):
                self.write_log(f"  • {host}\n")
        else:
            self.write_log("  None\n")

        if self.connection_counts:
            most_active_host, count = max(
                self.connection_counts.items(), key=lambda x: x[1]
            )
            self.write_log(
                f"\nMost active host in the last 10 seconds: {most_active_host} ({count} connections)\n"
            )
        else:
            self.write_log("\nNo connections recorded in the last 10 seconds\n")

        self.write_log(separator)