"""Forensic event logger — structured JSON audit trail."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

# Event type constants
EVENT_MODIFIED = "modified"
EVENT_CREATED = "created"
EVENT_DELETED = "deleted"


class EventLogger:
    """Append-only JSON event logger writing to daily log files.

    Log directory structure:
        logs/events_YYYY-MM-DD.json

    Each file contains a JSON array of event records.
    """

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

    def _get_log_path(self) -> str:
        """Return today's log file path."""
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return os.path.join(self.log_dir, f"events_{date_str}.json")

    def _load_events(self, log_path: str) -> list[dict]:
        """Load existing events from a log file."""
        if not os.path.exists(log_path):
            return []
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _save_events(self, log_path: str, events: list[dict]) -> None:
        """Write the full event list to the log file."""
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2, ensure_ascii=False)

    def log_event(
        self,
        event_type: str,
        file_path: str,
        old_hash: str | None = None,
        new_hash: str | None = None,
        file_size: int | None = None,
        severity: str = "NORMAL",
    ) -> dict:
        """Record a single integrity event.

        Args:
            event_type: One of EVENT_MODIFIED, EVENT_CREATED, EVENT_DELETED.
            file_path: Path of the affected file.
            old_hash: Previous hash (from baseline). None for created files.
            new_hash: Current hash (from disk). None for deleted files.
            file_size: Current file size in bytes. None for deleted files.
            severity: CRITICAL or NORMAL — based on file pattern matching.

        Returns:
            The event dict that was logged.
        """
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "file_path": file_path,
            "old_hash": old_hash,
            "new_hash": new_hash,
            "file_size": file_size,
            "severity": severity,
        }

        log_path = self._get_log_path()
        events = self._load_events(log_path)
        events.append(event)
        self._save_events(log_path, events)

        return event

    def read_all_events(self) -> list[dict]:
        """Read and merge events from all log files, sorted by timestamp."""
        all_events = []
        if not os.path.exists(self.log_dir):
            return all_events
        for filename in sorted(os.listdir(self.log_dir)):
            if filename.startswith("events_") and filename.endswith(".json"):
                path = os.path.join(self.log_dir, filename)
                all_events.extend(self._load_events(path))
        all_events.sort(key=lambda e: e.get("timestamp", ""))
        return all_events
