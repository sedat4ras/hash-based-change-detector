"""File Integrity Monitor (FIM) — CLI entry point.

Usage:
    python main.py setup                          Create a new baseline
    python main.py monitor                        Start real-time monitoring
    python main.py monitor --watch /etc --interval 10
    python main.py report                         View forensic event summary
    python main.py                                Interactive legacy menu
"""

import argparse

from fim import __version__
from fim.baseline import create_baseline
from fim.monitor import start_monitoring
from fim.reporter import generate_report
from fim.config_loader import load_config, merge_cli_overrides

# --- DEFAULTS ---
DEFAULT_FOLDER = "monitored_files"
DEFAULT_BASELINE = "baseline.txt"
DEFAULT_LOG_DIR = "logs"


def legacy_menu() -> None:
    """Original interactive menu for backward compatibility."""
    config = load_config()

    print("-" * 40)
    print(f"FILE INTEGRITY MONITOR (FIM) v{__version__}")
    print("-" * 40)
    print("1. Create New Baseline (Setup)")
    print("2. Start Monitoring (Defend)")
    print("3. View Event Report (Forensics)")
    print("-" * 40)

    choice = input("Select an option (1, 2 or 3): ")

    if choice == "1":
        create_baseline(
            config.monitored_paths, config.baseline_file,
            exclude_patterns=config.exclude_patterns,
        )
    elif choice == "2":
        start_monitoring(
            config.monitored_paths, config.baseline_file,
            config.log_dir, config.polling_interval,
            config.exclude_patterns, config.critical_patterns,
        )
    elif choice == "3":
        generate_report(config.log_dir)
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
        "--watch", help="Override: scan this single directory",
    )
    sp.add_argument(
        "--exclude", help="Override: add exclusion glob pattern",
    )
    sp.add_argument(
        "--baseline", default=None,
        help="Baseline output file",
    )
    sp.add_argument(
        "--config", default="config.yml",
        help="Path to config file (default: config.yml)",
    )

    # monitor
    mp = subparsers.add_parser("monitor", help="Start real-time monitoring")
    mp.add_argument(
        "--watch", help="Override: monitor this single directory",
    )
    mp.add_argument(
        "--exclude", help="Override: add exclusion glob pattern",
    )
    mp.add_argument(
        "--interval", type=float, default=None,
        help="Override: scan interval in seconds",
    )
    mp.add_argument(
        "--baseline", default=None,
        help="Baseline file to use",
    )
    mp.add_argument(
        "--log-dir", default=None,
        help="Event log directory",
    )
    mp.add_argument(
        "--config", default="config.yml",
        help="Path to config file (default: config.yml)",
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

    if args.command == "report":
        generate_report(args.log_dir)
        return

    # Load config and apply CLI overrides for setup/monitor
    config = load_config(args.config)
    config = merge_cli_overrides(config, args)

    if args.command == "setup":
        create_baseline(
            config.monitored_paths, config.baseline_file,
            exclude_patterns=config.exclude_patterns,
        )
    elif args.command == "monitor":
        start_monitoring(
            config.monitored_paths, config.baseline_file,
            config.log_dir, config.polling_interval,
            config.exclude_patterns, config.critical_patterns,
        )


if __name__ == "__main__":
    main()
