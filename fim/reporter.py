"""Event log reporter — forensic summary of all recorded events."""

from __future__ import annotations

from collections import Counter

from fim.event_logger import EventLogger


def generate_report(log_dir: str = "logs") -> None:
    """Read all event logs and print a summary table.

    Shows:
    - Total events by type (modified, created, deleted)
    - Top 5 most frequently changed files
    - Date range of events
    """
    logger = EventLogger(log_dir=log_dir)
    events = logger.read_all_events()

    if not events:
        print("\n[INFO] No events recorded yet.")
        print("Run monitoring first to generate event data.")
        return

    # Count by type
    type_counts = Counter(e["event_type"] for e in events)

    # Top changed files
    file_counts = Counter(e["file_path"] for e in events)
    top_files = file_counts.most_common(5)

    # Date range
    timestamps = [e["timestamp"] for e in events if e.get("timestamp")]
    first = timestamps[0][:19] if timestamps else "N/A"
    last = timestamps[-1][:19] if timestamps else "N/A"

    # Print report
    print("\n" + "=" * 55)
    print("  FORENSIC AUDIT TRAIL — EVENT SUMMARY")
    print("=" * 55)

    print(f"\n  Period: {first} → {last}")
    print(f"  Total Events: {len(events)}")

    print("\n  Events by Type:")
    print("  " + "-" * 35)
    for etype in ["modified", "created", "deleted"]:
        count = type_counts.get(etype, 0)
        bar = "#" * min(count, 30)
        print(f"  {etype:<12} {count:>5}  {bar}")

    if top_files:
        print("\n  Most Frequently Changed Files:")
        print("  " + "-" * 45)
        for filepath, count in top_files:
            # Truncate long paths
            display = filepath if len(filepath) <= 40 else "..." + filepath[-37:]
            print(f"  {display:<42} {count:>3}x")

    print("\n  Log Directory: " + log_dir + "/")
    print("=" * 55 + "\n")
