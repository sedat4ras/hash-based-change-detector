"""Tests for the reporter module."""

from fim.event_logger import EventLogger, EVENT_MODIFIED, EVENT_CREATED, EVENT_DELETED
from fim.reporter import generate_report


class TestGenerateReport:
    def test_empty_report_no_crash(self, log_dir, capsys):
        """Report on empty logs should print info message."""
        generate_report(log_dir=log_dir)
        output = capsys.readouterr().out
        assert "No events recorded" in output

    def test_report_shows_event_counts(self, log_dir, capsys):
        """Report should show event type breakdown."""
        logger = EventLogger(log_dir=log_dir)
        logger.log_event(EVENT_MODIFIED, "a.txt", "old", "new")
        logger.log_event(EVENT_MODIFIED, "b.txt", "old", "new")
        logger.log_event(EVENT_CREATED, "c.txt", new_hash="hash")
        logger.log_event(EVENT_DELETED, "d.txt", old_hash="hash")

        generate_report(log_dir=log_dir)
        output = capsys.readouterr().out

        assert "modified" in output
        assert "created" in output
        assert "deleted" in output
        assert "Total Events: 4" in output

    def test_report_shows_most_changed_files(self, log_dir, capsys):
        """Report should show the most frequently changed files."""
        logger = EventLogger(log_dir=log_dir)
        # Change the same file 3 times
        for i in range(3):
            logger.log_event(EVENT_MODIFIED, "hotfile.txt", f"old{i}", f"new{i}")
        logger.log_event(EVENT_CREATED, "other.txt", new_hash="hash")

        generate_report(log_dir=log_dir)
        output = capsys.readouterr().out

        assert "hotfile.txt" in output
        assert "Most Frequently Changed" in output

    def test_report_shows_header(self, log_dir, capsys):
        """Report should show the forensic audit trail header."""
        logger = EventLogger(log_dir=log_dir)
        logger.log_event(EVENT_CREATED, "test.txt", new_hash="abc")

        generate_report(log_dir=log_dir)
        output = capsys.readouterr().out

        assert "FORENSIC AUDIT TRAIL" in output
