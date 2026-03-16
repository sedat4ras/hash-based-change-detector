"""Baseline creation and loading for file integrity monitoring."""

from __future__ import annotations

import os

from fim.hasher import calculate_hash


def create_baseline(
    monitored_folder: str,
    baseline_file: str,
    verbose: bool = True,
) -> dict[str, str]:
    """Scan a directory tree and write a baseline file.

    Args:
        monitored_folder: Root directory to scan.
        baseline_file: Output path for the pipe-delimited baseline.
        verbose: If True, print progress to stdout.

    Returns:
        Dict mapping file_path -> hash for all scanned files.
    """
    baseline = {}

    if os.path.exists(baseline_file):
        os.remove(baseline_file)

    if verbose:
        print(f"\n[INFO] Creating baseline from: {monitored_folder}...")

    with open(baseline_file, "w", encoding="utf-8") as f:
        for root, dirs, files in os.walk(monitored_folder):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                file_hash = calculate_hash(file_path)
                if file_hash:
                    f.write(f"{file_path}|{file_hash}\n")
                    baseline[file_path] = file_hash
                    if verbose:
                        print(f"[+] Added to baseline: {file_path}")

    if verbose:
        print(f"\n[SUCCESS] Baseline created: {baseline_file}")
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
