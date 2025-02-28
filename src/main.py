import argparse
import sys
import logging
from datetime import datetime

from src.processing.batch_processor import process_batch
from src.processing.stream_processor import process_stream

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_datetime(dt_str):
    """Convert datetime string to datetime object."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except ValueError:
        # Try different format if ISO format fails
        try:
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError(
                f"Invalid datetime format: {dt_str}. Use ISO format (YYYY-MM-DDTHH:MM:SS) or 'YYYY-MM-DD HH:MM:SS'"
            )


def main():
    parser = argparse.ArgumentParser(description="Log file connection analyzer")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Batch processing command
    batch_parser = subparsers.add_parser(
        "batch", help="Process a log file with time range"
    )
    batch_parser.add_argument("file", help="Log file to process")
    batch_parser.add_argument(
        "--host", required=True, help="Hostname to analyze"
    )
    batch_parser.add_argument("--start", help="Start datetime (ISO format)")
    batch_parser.add_argument("--end", help="End datetime (ISO format)")

    # Stream processing command
    stream_parser = subparsers.add_parser(
        "stream", help="Process a log file in real-time"
    )
    stream_parser.add_argument("file", help="Log file to monitor")
    stream_parser.add_argument(
        "--host", required=True, help="Hostname to track connections to"
    )
    stream_parser.add_argument(
        "--from-host", help="Hostname to track connections from"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "batch":
            start_time = parse_datetime(args.start) if args.start else None
            end_time = parse_datetime(args.end) if args.end else None

            connected_hosts = process_batch(
                args.file, args.host, start_time, end_time
            )

            if connected_hosts:
                print(f"Hosts connected to {args.host}:")
                for host in sorted(connected_hosts):
                    print(host)
            else:
                print(
                    f"No hosts connected to {args.host} in the specified time range."
                )

        elif args.command == "stream":
            process_stream(args.file, args.host, args.from_host)

    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
