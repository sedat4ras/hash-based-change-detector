"""Tests for the filter engine module."""

import os

from fim.filter_engine import (
    should_exclude,
    classify_severity,
    filter_walk,
    SEVERITY_CRITICAL,
    SEVERITY_NORMAL,
)


class TestShouldExclude:
    def test_log_files_excluded(self):
        assert should_exclude("app.log", ["*.log"]) is True

    def test_nested_log_excluded(self):
        assert should_exclude("path/to/debug.log", ["*.log"]) is True

    def test_tmp_files_excluded(self):
        assert should_exclude("temp.tmp", ["*.tmp"]) is True

    def test_pyc_files_excluded(self):
        assert should_exclude("module.pyc", ["*.pyc"]) is True

    def test_normal_file_not_excluded(self):
        assert should_exclude("important.conf", ["*.log", "*.tmp"]) is False

    def test_pycache_dir_excluded(self):
        assert should_exclude("__pycache__", ["__pycache__"]) is True

    def test_no_patterns_nothing_excluded(self):
        assert should_exclude("anything.txt", []) is False

    def test_swp_files_excluded(self):
        assert should_exclude(".file.swp", ["*.swp"]) is True


class TestClassifySeverity:
    def test_conf_file_is_critical(self):
        assert classify_severity("nginx.conf", ["*.conf"]) == SEVERITY_CRITICAL

    def test_env_file_is_critical(self):
        assert classify_severity(".env", ["*.env"]) == SEVERITY_CRITICAL

    def test_pem_file_is_critical(self):
        assert classify_severity("server.pem", ["*.pem"]) == SEVERITY_CRITICAL

    def test_passwd_substring_is_critical(self):
        assert classify_severity("shadow-passwd-backup", ["*passwd*"]) == SEVERITY_CRITICAL

    def test_shadow_is_critical(self):
        assert classify_severity("shadow", ["*shadow*"]) == SEVERITY_CRITICAL

    def test_normal_file_is_normal(self):
        assert classify_severity("readme.md", ["*.conf", "*.env"]) == SEVERITY_NORMAL

    def test_no_patterns_is_normal(self):
        assert classify_severity("anything.txt", []) == SEVERITY_NORMAL

    def test_key_file_is_critical(self):
        assert classify_severity("private.key", ["*.key"]) == SEVERITY_CRITICAL

    def test_nested_path_critical(self):
        assert classify_severity("/etc/nginx/nginx.conf", ["*.conf"]) == SEVERITY_CRITICAL


class TestFilterWalk:
    def test_returns_all_without_patterns(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        result = filter_walk(str(tmp_path), [])
        assert len(result) == 2

    def test_excludes_log_files(self, tmp_path):
        (tmp_path / "app.log").write_text("log")
        (tmp_path / "data.txt").write_text("data")
        result = filter_walk(str(tmp_path), ["*.log"])
        assert len(result) == 1
        assert result[0].endswith("data.txt")

    def test_prunes_excluded_directories(self, tmp_path):
        cache_dir = tmp_path / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "module.pyc").write_text("bytecode")
        (tmp_path / "main.py").write_text("code")
        result = filter_walk(str(tmp_path), ["__pycache__"])
        assert len(result) == 1
        assert result[0].endswith("main.py")

    def test_multiple_exclusion_patterns(self, tmp_path):
        (tmp_path / "app.log").write_text("log")
        (tmp_path / "temp.tmp").write_text("tmp")
        (tmp_path / "real.txt").write_text("real")
        result = filter_walk(str(tmp_path), ["*.log", "*.tmp"])
        assert len(result) == 1
        assert result[0].endswith("real.txt")

    def test_empty_directory(self, tmp_path):
        result = filter_walk(str(tmp_path), [])
        assert result == []

    def test_nested_files_included(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "nested.txt").write_text("nested")
        (tmp_path / "root.txt").write_text("root")
        result = filter_walk(str(tmp_path), [])
        assert len(result) == 2


class TestSeverityInEvents:
    """Integration: verify severity flows through to events."""

    def test_critical_file_event_has_severity(self, tmp_path):
        from fim.baseline import create_baseline
        from fim.event_logger import EventLogger
        from fim.monitor import _run_single_scan

        monitored = tmp_path / "monitored"
        monitored.mkdir()
        (monitored / "app.conf").write_text("original config")

        baseline_file = str(tmp_path / "baseline.txt")
        log_dir = str(tmp_path / "logs")

        baseline = create_baseline(
            str(monitored), baseline_file, verbose=False,
        )
        logger = EventLogger(log_dir=log_dir)

        # Modify the critical file
        (monitored / "app.conf").write_text("modified config")

        _run_single_scan(
            [str(monitored)], baseline, logger,
            critical_patterns=["*.conf"],
        )

        events = logger.read_all_events()
        assert len(events) == 1
        assert events[0]["severity"] == SEVERITY_CRITICAL

    def test_normal_file_event_has_normal_severity(self, tmp_path):
        from fim.baseline import create_baseline
        from fim.event_logger import EventLogger
        from fim.monitor import _run_single_scan

        monitored = tmp_path / "monitored"
        monitored.mkdir()
        (monitored / "readme.md").write_text("original")

        baseline_file = str(tmp_path / "baseline.txt")
        log_dir = str(tmp_path / "logs")

        baseline = create_baseline(
            str(monitored), baseline_file, verbose=False,
        )
        logger = EventLogger(log_dir=log_dir)

        (monitored / "readme.md").write_text("modified")

        _run_single_scan(
            [str(monitored)], baseline, logger,
            critical_patterns=["*.conf"],
        )

        events = logger.read_all_events()
        assert len(events) == 1
        assert events[0]["severity"] == SEVERITY_NORMAL
