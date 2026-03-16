"""Filter engine — glob-based exclusion and severity classification."""

from __future__ import annotations

import fnmatch
import os

# Severity levels
SEVERITY_CRITICAL = "CRITICAL"
SEVERITY_NORMAL = "NORMAL"


def should_exclude(file_path: str, exclude_patterns: list[str]) -> bool:
    """Determine if a file should be excluded from monitoring.

    Matches the file's basename AND the full path against each glob
    pattern. This allows both simple patterns like "*.log" and path
    patterns like "__pycache__/*".

    Args:
        file_path: The file path to check.
        exclude_patterns: List of glob patterns.

    Returns:
        True if the file matches any exclusion pattern.
    """
    basename = os.path.basename(file_path)
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(basename, pattern):
            return True
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False


def classify_severity(file_path: str, critical_patterns: list[str]) -> str:
    """Classify a file's severity based on critical patterns.

    Args:
        file_path: The file path to classify.
        critical_patterns: List of glob patterns for critical files.

    Returns:
        SEVERITY_CRITICAL or SEVERITY_NORMAL.
    """
    basename = os.path.basename(file_path)
    for pattern in critical_patterns:
        if fnmatch.fnmatch(basename, pattern):
            return SEVERITY_CRITICAL
        if fnmatch.fnmatch(file_path, pattern):
            return SEVERITY_CRITICAL
    return SEVERITY_NORMAL


def filter_walk(
    directory: str,
    exclude_patterns: list[str],
) -> list[str]:
    """Walk a directory and return file paths not matching exclusion patterns.

    Prunes excluded directories to avoid descending into them.

    Args:
        directory: Root directory to walk.
        exclude_patterns: Glob patterns for files/dirs to skip.

    Returns:
        List of non-excluded file paths.
    """
    result = []
    for root, dirs, files in os.walk(directory):
        # Prune excluded directories in-place
        dirs[:] = [
            d for d in dirs
            if not should_exclude(d, exclude_patterns)
        ]
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if not should_exclude(file_path, exclude_patterns):
                result.append(file_path)
    return result
