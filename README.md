# Log Parser
A command-line tool for analyzing connection logs in both batch and real-time streaming modes.

## Features
- **Batch Processing**: Analyze log files within specified time ranges
- **Real-time Monitoring**: Watch directories for new log files and monitor connections
- **Flexible Time Filtering**: Filter connections by start and end times
- **Connection Statistics**: Track connections to/from specific hosts
- **Activity Reports**: Generate periodic reports of connection activities
## Installation
### Prerequisites
- Python 3.6 or higher
- pip (Python package installer)
- pytest
### Installing from Source
1. Clone the repository:
```bash
git clone https://github.com/peekknuf/Clarity-Log-Parsing-CLI
cd Clarity-Log-Parsing-CLI
```
2. Install in development mode:
```bash
pip install -e .
```
## Usage
The tool provides two main commands: `batch` and `stream`.
### Batch Processing
Process a single log file to analyze connections:
```bash
log-parser batch path/to/logfile.log --host target-host [--start "2024-01-01 00:00:00"] [--end "2024-01-02 00:00:00"]
```
An example command that outputs all the connections to host27 without specific timeframe.
```bash
log-parser batch logs/Optional-connections.log --host host27
```
Options:
- `--host`: Required. The hostname to analyze connections to
- `--start`: Optional. Start time in either format:
  - ISO format with optional timezone (e.g., "2024-01-01T00:00:00" or "2024-01-01T00:00:00Z")
  - Simple format without timezone (e.g., "2024-01-01 00:00:00")
- `--end`: Optional. End time (same format options as --start)
### Stream Processing
Monitor a directory for log files in real-time:
```bash
log-parser stream path/to/log/directory --host target-host [--from-host source-host]
```
This command will be monitoring logs directory for new incoming .log files and scanning them, but would also check the NEW records appended to the existing files.
At certain, even the most minimal, scale the output of those reports should be stored somewhere, terminal session is def not it, it's fine for a MVP though.
Also, yes, it's doing every 10 sec instead of every 1 hr because it's easier to test that way. Not a big deal. 
```bash
log-parser stream logs --host host27
```
Example output:
```bash
2025-03-01 08:57:34,039 - INFO - Starting real-time monitoring of directory: logs
2025-03-01 08:57:34,039 - INFO - Tracking connections to host27
2025-03-01 08:57:34,039 - INFO - Press Ctrl+C to stop monitoring
2025-03-01 08:57:35,043 - INFO - Found new log file: logs/Optional-connections.log

==================================================
REPORT: 2025-03-01 08:57:44
==================================================

Hosts connected TO host27 in the last 10 seconds:
  None

Hosts that received connections FROM host27 in the last 10 seconds:
  None

No connections recorded in the last 10 seconds
==================================================
```
Options:
- `--host`: Required. The hostname to track connections to
- `--from-host`: Optional. Track connections from this specific host


## Log File Format
The log files should follow this format:
```
<unix_timestamp> <source_host> <destination_host>
```
Example:
```
1704068314 host22 host29
1704072476 host74 host35
```

## Development
### Setting up Development Environment
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate 
```
2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Running Tests
Run the test suite:
```bash
pytest
```
### Code Structure
- `src/`  
  - `parser/`: Log parsing functionality
  - `processing/`: Batch and stream processing logic  
  - `utils/`: Utility functions
- `tests/`: Test suite
- `cli.py`: The entrypoint to command-line interface

## Contributing (kinda optimistic ngl)
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite
5. Submit a pull request

## License

Meh

 

