"""File Integrity Monitor (FIM) — CLI entry point.

Usage:
    python main.py setup              Create a new baseline
    python main.py monitor            Start real-time monitoring
    python main.py report             View forensic event summary
    python main.py                    Interactive legacy menu
"""

import argparse
import sys

from fim import __version__
from fim.baseline import create_baseline
from fim.monitor import start_monitoring
from fim.reporter import generate_report

# --- DEFAULTS ---
DEFAULT_FOLDER = "monitored_files"
DEFAULT_BASELINE = "baseline.txt"
DEFAULT_LOG_DIR = "logs"


def legacy_menu() -> None:
    """Original interactive menu for backward compatibility."""
    print("-" * 40)
    print(f"FILE INTEGRITY MONITOR (FIM) v{__version__}")
    print("-" * 40)
    print("1. Create New Baseline (Setup)")
    print("2. Start Monitoring (Defend)")
    print("3. View Event Report (Forensics)")
    print("-" * 40)

    choice = input("Select an option (1, 2 or 3): ")

    if choice == "1":
        create_baseline(DEFAULT_FOLDER, DEFAULT_BASELINE)
    elif choice == "2":
        start_monitoring(DEFAULT_FOLDER, DEFAULT_BASELINE, DEFAULT_LOG_DIR)
    elif choice == "3":
        generate_report(DEFAULT_LOG_DIR)
    else:
        print("Invalid choice. Exiting.")


def main() -> None:
    """Parse CLI arguments and dispatch commands."""
    parser = argparse.ArgumentParser(
        description="File Integrity Monitor (FIM) — detect file tampering in real time",
        prog="fim",
    )
    parser.add_argument(
        "--version", action="version", version=f"FIM v{__version__}"
    )

    subparsers = parser.add_subparsers(dest="command")

    # setup
    sp = subparsers.add_parser("setup", help="Create a new baseline")
    sp.add_argument(
        "--folder", default=DEFAULT_FOLDER,
        help=f"Directory to scan (default: {DEFAULT_FOLDER})",
    )
    sp.add_argument(
        "--baseline", default=DEFAULT_BASELINE,
        help=f"Baseline output file (default: {DEFAULT_BASELINE})",
    )

    # monitor
    mp = subparsers.add_parser("monitor", help="Start real-time monitoring")
    mp.add_argument(
        "--folder", default=DEFAULT_FOLDER,
        help=f"Directory to monitor (default: {DEFAULT_FOLDER})",
    )
    mp.add_argument(
        "--baseline", default=DEFAULT_BASELINE,
        help=f"Baseline file to use (default: {DEFAULT_BASELINE})",
    )
    mp.add_argument(
        "--log-dir", default=DEFAULT_LOG_DIR,
        help=f"Event log directory (default: {DEFAULT_LOG_DIR})",
    )
    mp.add_argument(
        "--interval", type=float, default=1.0,
        help="Scan interval in seconds (default: 1.0)",
    )

    # report
    rp = subparsers.add_parser("report", help="View forensic event summary")
    rp.add_argument(
        "--log-dir", default=DEFAULT_LOG_DIR,
        help=f"Event log directory (default: {DEFAULT_LOG_DIR})",
    )

    args = parser.parse_args()

    # No subcommand → fall back to interactive menu
    if args.command is None:
        legacy_menu()
        return

    if args.command == "setup":
        create_baseline(args.folder, args.baseline)
    elif args.command == "monitor":
        start_monitoring(
            args.folder, args.baseline, args.log_dir, args.interval,
        )
    elif args.command == "report":
        generate_report(args.log_dir)


if __name__ == "__main__":
    main()
