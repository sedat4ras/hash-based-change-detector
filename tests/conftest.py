"""Shared pytest fixtures for FIM tests."""

import os
import pytest


@pytest.fixture
def sample_dir(tmp_path):
    """Create a temporary directory with sample files for testing."""
    d = tmp_path / "monitored"
    d.mkdir()
    (d / "file1.txt").write_text("Hello World")
    (d / "file2.txt").write_text("Secret Data 123")
    sub = d / "subdir"
    sub.mkdir()
    (sub / "nested.txt").write_text("Nested content")
    return str(d)


@pytest.fixture
def baseline_file(tmp_path):
    """Return a path for a temporary baseline file."""
    return str(tmp_path / "baseline.txt")


@pytest.fixture
def log_dir(tmp_path):
    """Return a path for a temporary log directory."""
    d = tmp_path / "logs"
    d.mkdir()
    return str(d)
