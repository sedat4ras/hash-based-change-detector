"""Baseline creation and loading for file integrity monitoring."""

from __future__ import annotations

import os

from fim.hasher import calculate_hash
from fim.filter_engine import filter_walk


def create_baseline(
    monitored_paths: list[str] | str,
    baseline_file: str,
    verbose: bool = True,
    exclude_patterns: list[str] | None = None,
) -> dict[str, str]:
    """Scan directory trees and write a baseline file.

    Args:
        monitored_paths: Directory or list of directories to scan.
        baseline_file: Output path for the pipe-delimited baseline.
        verbose: If True, print progress to stdout.
        exclude_patterns: Glob patterns to exclude from scanning.

    Returns:
        Dict mapping file_path -> hash for all scanned files.
    """
    # Accept single string for backward compatibility
    if isinstance(monitored_paths, str):
        monitored_paths = [monitored_paths]

    exclude = exclude_patterns or []
    baseline = {}

    if os.path.exists(baseline_file):
        os.remove(baseline_file)

    if verbose:
        dirs_str = ", ".join(monitored_paths)
        print(f"\n[INFO] Creating baseline from: {dirs_str}...")

    with open(baseline_file, "w", encoding="utf-8") as f:
        for directory in monitored_paths:
            if not os.path.isdir(directory):
                if verbose:
                    print(f"[WARN] Directory not found: {directory}")
                continue

            file_paths = filter_walk(directory, exclude)
            for file_path in file_paths:
                file_hash = calculate_hash(file_path)
                if file_hash:
                    f.write(f"{file_path}|{file_hash}\n")
                    baseline[file_path] = file_hash
                    if verbose:
                        print(f"[+] Added to baseline: {file_path}")

    if verbose:
        print(f"\n[SUCCESS] Baseline created: {baseline_file}")
        print(f"  Files indexed: {len(baseline)}")
        print("You can now start monitoring.")

    return baseline


def load_baseline(baseline_file: str) -> dict[str, str]:
    """Load a baseline file into a dictionary.

    Args:
        baseline_file: Path to the pipe-delimited baseline file.

    Returns:
        Dict mapping file_path -> hash.

    Raises:
        FileNotFoundError: If baseline_file does not exist.
    """
    if not os.path.exists(baseline_file):
        raise FileNotFoundError(
            f"Baseline file not found: {baseline_file}. "
            "Please create a baseline first (run: python main.py setup)."
        )

    baseline = {}
    with open(baseline_file, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) == 2:
                file_path, file_hash = parts
                baseline[file_path] = file_hash
    return baseline
