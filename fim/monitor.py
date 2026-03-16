"""Core monitoring loop with modification, creation, and deletion detection."""

from __future__ import annotations

import os
import time

from fim.hasher import calculate_hash
from fim.baseline import load_baseline
from fim.event_logger import EventLogger, EVENT_MODIFIED, EVENT_CREATED, EVENT_DELETED
from fim.filter_engine import filter_walk, classify_severity, SEVERITY_CRITICAL

# ANSI colors
RED = "\033[91m"
RESET = "\033[0m"


def _get_file_size(file_path: str) -> int | None:
    """Return file size in bytes, or None if file is inaccessible."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return None


def _print_alert(event: dict) -> None:
    """Print a console alert with severity coloring."""
    etype = event["event_type"]
    fpath = event["file_path"]
    severity = event.get("severity", "NORMAL")

    prefix = f"{RED}[CRITICAL]{RESET} " if severity == SEVERITY_CRITICAL else ""

    if etype == EVENT_MODIFIED:
        print(f"\n{prefix}[!!! ALERT !!!] FILE CHANGED: {fpath}")
        print(f"   Old Hash: {event['old_hash']}")
        print(f"   New Hash: {event['new_hash']}")
    elif etype == EVENT_CREATED:
        print(f"\n{prefix}[!!! ALERT !!!] NEW FILE DETECTED: {fpath}")
    elif etype == EVENT_DELETED:
        print(f"\n{prefix}[!!! ALERT !!!] FILE DELETED: {fpath}")
        print(f"   Last Known Hash: {event['old_hash']}")


def _run_single_scan(
    monitored_paths: list[str],
    baseline_hashes: dict[str, str],
    logger: EventLogger,
    exclude_patterns: list[str] | None = None,
    critical_patterns: list[str] | None = None,
) -> None:
    """Execute one scan cycle: detect modifications, creations, deletions.

    Modifies baseline_hashes in place (updates on change, adds new,
    removes deleted) to avoid repeated alerts.
    """
    exclude = exclude_patterns or []
    critical = critical_patterns or []
    current_files_on_disk: set[str] = set()

    # Pass 1: Walk disk — detect modifications and new files
    for directory in monitored_paths:
        if not os.path.isdir(directory):
            continue

        file_paths = filter_walk(directory, exclude)
        for file_path in file_paths:
            current_files_on_disk.add(file_path)
            current_hash = calculate_hash(file_path)

            if current_hash is None:
                continue  # File disappeared between walk and hash

            severity = classify_severity(file_path, critical)

            if file_path in baseline_hashes:
                stored_hash = baseline_hashes[file_path]
                if current_hash != stored_hash:
                    event = logger.log_event(
                        event_type=EVENT_MODIFIED,
                        file_path=file_path,
                        old_hash=stored_hash,
                        new_hash=current_hash,
                        file_size=_get_file_size(file_path),
                        severity=severity,
                    )
                    _print_alert(event)
                    baseline_hashes[file_path] = current_hash
            else:
                event = logger.log_event(
                    event_type=EVENT_CREATED,
                    file_path=file_path,
                    new_hash=current_hash,
                    file_size=_get_file_size(file_path),
                    severity=severity,
                )
                _print_alert(event)
                baseline_hashes[file_path] = current_hash

    # Pass 2: Check baseline for deletions
    deleted_files = set(baseline_hashes.keys()) - current_files_on_disk
    for file_path in deleted_files:
        severity = classify_severity(file_path, critical)
        event = logger.log_event(
            event_type=EVENT_DELETED,
            file_path=file_path,
            old_hash=baseline_hashes[file_path],
            severity=severity,
        )
        _print_alert(event)

    # Remove deleted entries after iteration
    for file_path in deleted_files:
        del baseline_hashes[file_path]


def start_monitoring(
    monitored_paths: list[str] | str,
    baseline_file: str,
    log_dir: str = "logs",
    interval: float = 1.0,
    exclude_patterns: list[str] | None = None,
    critical_patterns: list[str] | None = None,
) -> None:
    """Continuously monitor files against the baseline.

    Runs an infinite loop (until KeyboardInterrupt) that detects:
    - File modifications (hash mismatch)
    - New file creations (not in baseline)
    - File deletions (in baseline but not on disk)

    All events are logged to JSON and printed to console.

    Args:
        monitored_paths: Directory or list of directories to monitor.
        baseline_file: Path to the baseline file.
        log_dir: Directory for JSON event logs.
        interval: Seconds between scan cycles.
        exclude_patterns: Glob patterns to exclude from monitoring.
        critical_patterns: Glob patterns for CRITICAL severity files.
    """
    # Accept single string for backward compatibility
    if isinstance(monitored_paths, str):
        monitored_paths = [monitored_paths]

    dirs_str = ", ".join(monitored_paths)
    print(f"\n[INFO] Monitoring started on: {dirs_str}")
    print(f"[INFO] Scan interval: {interval}s")
    print(f"[INFO] Events logged to: {log_dir}/")
    if exclude_patterns:
        print(f"[INFO] Excluding: {', '.join(exclude_patterns)}")
    print("[INFO] Press Ctrl+C to stop...\n")

    baseline_hashes = load_baseline(baseline_file)
    logger = EventLogger(log_dir=log_dir)

    try:
        while True:
            time.sleep(interval)
            _run_single_scan(
                monitored_paths, baseline_hashes, logger,
                exclude_patterns, critical_patterns,
            )
    except KeyboardInterrupt:
        print("\n[INFO] Monitoring stopped by user.")
