import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import patch

from src.processing.stream_processor import (
    create_file_tracker,
    process_stream,
    generate_report
)

@pytest.fixture
def temp_log_dir():
    """Create a temporary directory with some log files."""
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
    with tempfile.NamedTemporaryFile() as tmp:
        tracker = create_file_tracker(tmp.name)
        
        assert isinstance(tracker, dict)
        assert "file_path" in tracker
        assert "last_position" in tracker
        assert "last_modified" in tracker
        assert tracker["last_position"] == 0
        assert tracker["file_path"] == tmp.name

def test_generate_report(capsys):
    target_host = "host1"
    connections_to = {"host2", "host3"}
    connections_from = {"host4", "host5"}
    connection_counts = {"host2": 3, "host3": 1, "host4": 2}
    
    generate_report(target_host, connections_to, connections_from, connection_counts)
    
    captured = capsys.readouterr()
    assert f"Hosts connected TO {target_host}" in captured.out
    assert "host2" in captured.out
    assert "host3" in captured.out
    assert "Most active host" in captured.out
    assert "host2 (3 connections)" in captured.out

def test_process_stream_new_file(temp_log_dir):
    log_dir, existing_files = temp_log_dir
    target_host = "host1"
    
    with patch('builtins.print'):  
        new_log_path = os.path.join(log_dir, "new.log")
        with open(new_log_path, "w") as f:
            now = int(datetime.now().timestamp())
            f.write(f"{now} host6 host1\n")

        process_stream(log_dir, target_host, max_iterations=2)

def test_process_stream_file_rotation(temp_log_dir):
    log_dir, existing_files = temp_log_dir
    target_host = "host1"
    
    with patch('builtins.print'):  # Suppress output
        with open(existing_files[0], "w") as f:
            now = int(datetime.now().timestamp())
            f.write(f"{now} host7 host1\n")
        
        process_stream(log_dir, target_host, max_iterations=2)





