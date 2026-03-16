"""Core monitoring loop with modification, creation, and deletion detection."""

from __future__ import annotations

import os
import time

from fim.hasher import calculate_hash
from fim.baseline import load_baseline
from fim.event_logger import EventLogger, EVENT_MODIFIED, EVENT_CREATED, EVENT_DELETED


def _get_file_size(file_path: str) -> int | None:
    """Return file size in bytes, or None if file is inaccessible."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return None


def _print_alert(event: dict) -> None:
    """Print a console alert matching the original output format."""
    etype = event["event_type"]
    fpath = event["file_path"]

    if etype == EVENT_MODIFIED:
        print(f"\n[!!! ALERT !!!] FILE CHANGED: {fpath}")
        print(f"   Old Hash: {event['old_hash']}")
        print(f"   New Hash: {event['new_hash']}")
    elif etype == EVENT_CREATED:
        print(f"\n[!!! ALERT !!!] NEW FILE DETECTED: {fpath}")
    elif etype == EVENT_DELETED:
        print(f"\n[!!! ALERT !!!] FILE DELETED: {fpath}")
        print(f"   Last Known Hash: {event['old_hash']}")


def _run_single_scan(
    monitored_folder: str,
    baseline_hashes: dict[str, str],
    logger: EventLogger,
) -> None:
    """Execute one scan cycle: detect modifications, creations, deletions.

    Modifies baseline_hashes in place (updates on change, adds new,
    removes deleted) to avoid repeated alerts.
    """
    current_files_on_disk: set[str] = set()

    # Pass 1: Walk disk — detect modifications and new files
    for root, dirs, files in os.walk(monitored_folder):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            current_files_on_disk.add(file_path)
            current_hash = calculate_hash(file_path)

            if current_hash is None:
                continue  # File disappeared between walk and hash

            if file_path in baseline_hashes:
                stored_hash = baseline_hashes[file_path]
                if current_hash != stored_hash:
                    event = logger.log_event(
                        event_type=EVENT_MODIFIED,
                        file_path=file_path,
                        old_hash=stored_hash,
                        new_hash=current_hash,
                        file_size=_get_file_size(file_path),
                    )
                    _print_alert(event)
                    baseline_hashes[file_path] = current_hash
            else:
                event = logger.log_event(
                    event_type=EVENT_CREATED,
                    file_path=file_path,
                    new_hash=current_hash,
                    file_size=_get_file_size(file_path),
                )
                _print_alert(event)
                baseline_hashes[file_path] = current_hash

    # Pass 2: Check baseline for deletions
    deleted_files = set(baseline_hashes.keys()) - current_files_on_disk
    for file_path in deleted_files:
        event = logger.log_event(
            event_type=EVENT_DELETED,
            file_path=file_path,
            old_hash=baseline_hashes[file_path],
        )
        _print_alert(event)

    # Remove deleted entries after iteration
    for file_path in deleted_files:
        del baseline_hashes[file_path]


def start_monitoring(
    monitored_folder: str,
    baseline_file: str,
    log_dir: str = "logs",
    interval: float = 1.0,
) -> None:
    """Continuously monitor files against the baseline.

    Runs an infinite loop (until KeyboardInterrupt) that detects:
    - File modifications (hash mismatch)
    - New file creations (not in baseline)
    - File deletions (in baseline but not on disk)

    All events are logged to JSON and printed to console.

    Args:
        monitored_folder: Root directory to monitor.
        baseline_file: Path to the baseline file.
        log_dir: Directory for JSON event logs.
        interval: Seconds between scan cycles.
    """
    print(f"\n[INFO] Monitoring started on: {monitored_folder}")
    print(f"[INFO] Events logged to: {log_dir}/")
    print("[INFO] Press Ctrl+C to stop...\n")

    baseline_hashes = load_baseline(baseline_file)
    logger = EventLogger(log_dir=log_dir)

    try:
        while True:
            time.sleep(interval)
            _run_single_scan(monitored_folder, baseline_hashes, logger)
    except KeyboardInterrupt:
        print("\n[INFO] Monitoring stopped by user.")
