"""Tests for the monitor module — especially deletion detection."""

import os

from fim.baseline import create_baseline
from fim.event_logger import EventLogger, EVENT_MODIFIED, EVENT_CREATED, EVENT_DELETED
from fim.monitor import _run_single_scan


class TestSingleScan:
    def test_no_changes_no_events(self, sample_dir, baseline_file, log_dir):
        """Unchanged files should produce no events."""
        baseline = create_baseline(sample_dir, baseline_file, verbose=False)
        logger = EventLogger(log_dir=log_dir)

        _run_single_scan(sample_dir, baseline, logger)

        events = logger.read_all_events()
        assert len(events) == 0

    def test_detect_modification(self, sample_dir, baseline_file, log_dir):
        """Modified file content should trigger a modified event."""
        baseline = create_baseline(sample_dir, baseline_file, verbose=False)
        logger = EventLogger(log_dir=log_dir)

        # Modify a file
        file1 = os.path.join(sample_dir, "file1.txt")
        with open(file1, "w") as f:
            f.write("Modified content")

        _run_single_scan(sample_dir, baseline, logger)

        events = logger.read_all_events()
        assert len(events) == 1
        assert events[0]["event_type"] == EVENT_MODIFIED
        assert events[0]["file_path"] == file1

    def test_detect_new_file(self, sample_dir, baseline_file, log_dir):
        """A new file should trigger a created event."""
        baseline = create_baseline(sample_dir, baseline_file, verbose=False)
        logger = EventLogger(log_dir=log_dir)

        # Create a new file
        new_file = os.path.join(sample_dir, "newfile.txt")
        with open(new_file, "w") as f:
            f.write("I am new")

        _run_single_scan(sample_dir, baseline, logger)

        events = logger.read_all_events()
        assert len(events) == 1
        assert events[0]["event_type"] == EVENT_CREATED
        assert events[0]["file_path"] == new_file

    def test_detect_deletion(self, sample_dir, baseline_file, log_dir):
        """A deleted file should trigger a deleted event."""
        baseline = create_baseline(sample_dir, baseline_file, verbose=False)
        logger = EventLogger(log_dir=log_dir)

        # Delete a file
        file2 = os.path.join(sample_dir, "file2.txt")
        os.remove(file2)

        _run_single_scan(sample_dir, baseline, logger)

        events = logger.read_all_events()
        assert len(events) == 1
        assert events[0]["event_type"] == EVENT_DELETED
        assert events[0]["file_path"] == file2

    def test_deletion_removes_from_baseline(self, sample_dir, baseline_file, log_dir):
        """After deletion, the file should be removed from baseline dict."""
        baseline = create_baseline(sample_dir, baseline_file, verbose=False)
        logger = EventLogger(log_dir=log_dir)

        file2 = os.path.join(sample_dir, "file2.txt")
        os.remove(file2)

        assert file2 in baseline
        _run_single_scan(sample_dir, baseline, logger)
        assert file2 not in baseline

    def test_no_repeat_alerts(self, sample_dir, baseline_file, log_dir):
        """After detecting a change, a second scan should not re-alert."""
        baseline = create_baseline(sample_dir, baseline_file, verbose=False)
        logger = EventLogger(log_dir=log_dir)

        # Modify a file
        file1 = os.path.join(sample_dir, "file1.txt")
        with open(file1, "w") as f:
            f.write("Changed once")

        _run_single_scan(sample_dir, baseline, logger)
        events1 = logger.read_all_events()
        assert len(events1) == 1

        # Second scan — no more changes
        _run_single_scan(sample_dir, baseline, logger)
        events2 = logger.read_all_events()
        assert len(events2) == 1  # Still just 1, no repeat

    def test_multiple_changes_single_scan(self, sample_dir, baseline_file, log_dir):
        """Multiple changes in one scan cycle should all be detected."""
        baseline = create_baseline(sample_dir, baseline_file, verbose=False)
        logger = EventLogger(log_dir=log_dir)

        # Modify file1
        file1 = os.path.join(sample_dir, "file1.txt")
        with open(file1, "w") as f:
            f.write("Changed")

        # Delete file2
        file2 = os.path.join(sample_dir, "file2.txt")
        os.remove(file2)

        # Create new file
        new_file = os.path.join(sample_dir, "added.txt")
        with open(new_file, "w") as f:
            f.write("New file")

        _run_single_scan(sample_dir, baseline, logger)

        events = logger.read_all_events()
        types = {e["event_type"] for e in events}
        assert types == {EVENT_MODIFIED, EVENT_CREATED, EVENT_DELETED}

    def test_modified_event_has_file_size(self, sample_dir, baseline_file, log_dir):
        """Modified events should include file_size."""
        baseline = create_baseline(sample_dir, baseline_file, verbose=False)
        logger = EventLogger(log_dir=log_dir)

        file1 = os.path.join(sample_dir, "file1.txt")
        with open(file1, "w") as f:
            f.write("New content here")

        _run_single_scan(sample_dir, baseline, logger)

        events = logger.read_all_events()
        assert events[0]["file_size"] is not None
        assert events[0]["file_size"] > 0

    def test_deleted_event_has_old_hash(self, sample_dir, baseline_file, log_dir):
        """Deleted events should include old_hash for forensics."""
        baseline = create_baseline(sample_dir, baseline_file, verbose=False)
        logger = EventLogger(log_dir=log_dir)

        file1 = os.path.join(sample_dir, "file1.txt")
        old_hash = baseline[file1]
        os.remove(file1)

        _run_single_scan(sample_dir, baseline, logger)

        events = logger.read_all_events()
        assert events[0]["old_hash"] == old_hash
