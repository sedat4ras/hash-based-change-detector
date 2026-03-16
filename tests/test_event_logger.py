"""Tests for the event logger module."""

import json
import os

from fim.event_logger import EventLogger, EVENT_MODIFIED, EVENT_CREATED, EVENT_DELETED


class TestEventLogger:
    def test_log_creates_file(self, log_dir):
        logger = EventLogger(log_dir=log_dir)
        logger.log_event(EVENT_MODIFIED, "test.txt", "old", "new", 100)
        files = os.listdir(log_dir)
        assert len(files) == 1
        assert files[0].startswith("events_")
        assert files[0].endswith(".json")

    def test_log_event_returns_dict(self, log_dir):
        logger = EventLogger(log_dir=log_dir)
        event = logger.log_event(EVENT_CREATED, "new.txt", new_hash="abc123")
        assert isinstance(event, dict)
        assert event["event_type"] == EVENT_CREATED
        assert event["file_path"] == "new.txt"
        assert event["new_hash"] == "abc123"

    def test_event_has_timestamp(self, log_dir):
        logger = EventLogger(log_dir=log_dir)
        event = logger.log_event(EVENT_MODIFIED, "test.txt", "old", "new")
        assert "timestamp" in event
        assert "T" in event["timestamp"]  # ISO 8601 format

    def test_event_has_all_fields(self, log_dir):
        logger = EventLogger(log_dir=log_dir)
        event = logger.log_event(
            EVENT_MODIFIED, "file.txt", "oldhash", "newhash", 2048,
        )
        expected_keys = {"timestamp", "event_type", "file_path",
                         "old_hash", "new_hash", "file_size", "severity"}
        assert set(event.keys()) == expected_keys

    def test_multiple_events_appended(self, log_dir):
        logger = EventLogger(log_dir=log_dir)
        logger.log_event(EVENT_CREATED, "a.txt", new_hash="hash1")
        logger.log_event(EVENT_MODIFIED, "b.txt", "old", "new")
        logger.log_event(EVENT_DELETED, "c.txt", old_hash="hash3")

        events = logger.read_all_events()
        assert len(events) == 3

    def test_log_file_is_valid_json(self, log_dir):
        logger = EventLogger(log_dir=log_dir)
        logger.log_event(EVENT_CREATED, "test.txt", new_hash="abc")

        log_path = logger._get_log_path()
        with open(log_path) as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) == 1

    def test_deleted_event_has_null_new_hash(self, log_dir):
        logger = EventLogger(log_dir=log_dir)
        event = logger.log_event(EVENT_DELETED, "gone.txt", old_hash="abc")
        assert event["new_hash"] is None
        assert event["file_size"] is None

    def test_created_event_has_null_old_hash(self, log_dir):
        logger = EventLogger(log_dir=log_dir)
        event = logger.log_event(EVENT_CREATED, "new.txt", new_hash="xyz", file_size=512)
        assert event["old_hash"] is None
        assert event["file_size"] == 512

    def test_read_all_events_empty(self, log_dir):
        logger = EventLogger(log_dir=log_dir)
        assert logger.read_all_events() == []

    def test_read_all_events_sorted_by_timestamp(self, log_dir):
        logger = EventLogger(log_dir=log_dir)
        logger.log_event(EVENT_CREATED, "first.txt", new_hash="a")
        logger.log_event(EVENT_MODIFIED, "second.txt", "b", "c")
        logger.log_event(EVENT_DELETED, "third.txt", old_hash="d")

        events = logger.read_all_events()
        timestamps = [e["timestamp"] for e in events]
        assert timestamps == sorted(timestamps)

    def test_creates_log_dir_if_missing(self, tmp_path):
        new_dir = str(tmp_path / "new_logs")
        logger = EventLogger(log_dir=new_dir)
        logger.log_event(EVENT_CREATED, "test.txt", new_hash="abc")
        assert os.path.exists(new_dir)

    def test_read_all_from_nonexistent_dir(self, tmp_path):
        logger = EventLogger(log_dir=str(tmp_path / "nope"))
        # Override log_dir to nonexistent without creating
        logger.log_dir = str(tmp_path / "nonexistent")
        assert logger.read_all_events() == []
