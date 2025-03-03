import pytest
import tempfile
import os
import time
import logging
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, call, MagicMock

from src.processing.stream_processor import (
    create_file_tracker,
    process_stream,
    generate_report
)

@pytest.fixture
def mock_logger():
    with patch('src.processing.stream_processor.logger') as mock_log:
        yield mock_log

@pytest.fixture
def temp_log_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        log_files = []
        log1_path = os.path.join(tmpdirname, "current.log")
        with open(log1_path, "w") as f:
            now = int(datetime.now().timestamp())
            f.write(f"{now} host1 host2\n")
            f.write(f"{now-30} host2 host1\n")
            f.write(f"{now-60} host3 host1\n")
        log_files.append(log1_path)
        yield tmpdirname, log_files

def test_create_file_tracker():
    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(b"test content\n")
        temp_file.flush()

        tracker = create_file_tracker(temp_file.name)

        assert tracker["file_path"] == temp_file.name
        assert tracker["last_position"] == 0
        assert isinstance(tracker["last_modified"], float)
        assert tracker["last_modified"] == os.path.getmtime(temp_file.name)

def test_generate_report():
    target_host = "host1"
    connections_to = {"host2", "host3"}
    connections_from = {"host4", "host5"}
    connection_counts = {"host2": 2, "host3": 1, "host4": 3}

    with patch('builtins.print') as mock_print:
        generate_report(target_host, connections_to, connections_from, connection_counts)

        calls = mock_print.call_args_list
        report_text = "\n".join(str(call.args[0]) for call in calls)

        assert target_host in report_text
        assert "host2" in report_text
        assert "host3" in report_text
        assert "host4" in report_text
        assert "host5" in report_text

@patch('time.sleep')
def test_process_stream_basic(mock_sleep, mock_logger, temp_log_dir):
    log_dir, existing_files = temp_log_dir
    target_host = "host1"

    process_stream(log_dir, target_host, max_iterations=1)

    assert mock_logger.info.call_count > 0
    mock_logger.info.assert_has_calls([
        call(f"Starting real-time monitoring of directory: {log_dir}"),
        call(f"Tracking connections to {target_host}")
    ], any_order=True)






