"""Main entry point for the log parsing application."""

import sys
from src.cli import cli_main
from src.tui import run_tui

def main():
    """Main entry point that decides whether to run CLI or TUI version."""
    if len(sys.argv) == 1:
        run_tui()
    else:
        cli_main()

if __name__ == "__main__":
    sys.exit(main())