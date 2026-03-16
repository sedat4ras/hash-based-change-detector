"""Tests for the config loader module."""

import os
from types import SimpleNamespace

from fim.config_loader import FIMConfig, load_config, merge_cli_overrides


class TestFIMConfig:
    def test_default_values(self):
        config = FIMConfig()
        assert config.monitored_paths == ["monitored_files"]
        assert config.exclude_patterns == []
        assert config.critical_patterns == []
        assert config.polling_interval == 5.0
        assert config.baseline_file == "baseline.txt"
        assert config.log_dir == "logs"


class TestLoadConfig:
    def test_returns_defaults_when_no_file(self, tmp_path):
        config = load_config(str(tmp_path / "nonexistent.yml"))
        assert config.monitored_paths == ["monitored_files"]
        assert config.polling_interval == 5.0

    def test_loads_from_yaml(self, tmp_path):
        yaml_file = tmp_path / "config.yml"
        yaml_file.write_text(
            "monitored_paths:\n"
            "  - /var/www\n"
            "  - /etc/nginx\n"
            "exclude_patterns:\n"
            '  - "*.log"\n'
            "critical_patterns:\n"
            '  - "*.conf"\n'
            "polling_interval: 10\n"
            "baseline_file: custom_baseline.txt\n"
            "log_dir: custom_logs\n"
        )
        config = load_config(str(yaml_file))
        assert config.monitored_paths == ["/var/www", "/etc/nginx"]
        assert config.exclude_patterns == ["*.log"]
        assert config.critical_patterns == ["*.conf"]
        assert config.polling_interval == 10.0
        assert config.baseline_file == "custom_baseline.txt"
        assert config.log_dir == "custom_logs"

    def test_partial_yaml_fills_defaults(self, tmp_path):
        yaml_file = tmp_path / "config.yml"
        yaml_file.write_text("polling_interval: 15\n")
        config = load_config(str(yaml_file))
        assert config.polling_interval == 15.0
        assert config.monitored_paths == ["monitored_files"]  # default
        assert config.exclude_patterns == []  # default

    def test_empty_yaml_returns_defaults(self, tmp_path):
        yaml_file = tmp_path / "config.yml"
        yaml_file.write_text("")
        config = load_config(str(yaml_file))
        assert config.monitored_paths == ["monitored_files"]


class TestMergeCLIOverrides:
    def test_watch_overrides_paths(self):
        config = FIMConfig(monitored_paths=["/var/www"])
        args = SimpleNamespace(watch="/tmp/test", exclude=None, interval=None,
                               baseline=None, log_dir=None)
        merged = merge_cli_overrides(config, args)
        assert merged.monitored_paths == ["/tmp/test"]

    def test_exclude_appends(self):
        config = FIMConfig(exclude_patterns=["*.log"])
        args = SimpleNamespace(watch=None, exclude="*.tmp", interval=None,
                               baseline=None, log_dir=None)
        merged = merge_cli_overrides(config, args)
        assert "*.log" in merged.exclude_patterns
        assert "*.tmp" in merged.exclude_patterns

    def test_interval_overrides(self):
        config = FIMConfig(polling_interval=5.0)
        args = SimpleNamespace(watch=None, exclude=None, interval=10.0,
                               baseline=None, log_dir=None)
        merged = merge_cli_overrides(config, args)
        assert merged.polling_interval == 10.0

    def test_no_overrides_preserves_config(self):
        config = FIMConfig(
            monitored_paths=["/var/www"],
            exclude_patterns=["*.log"],
            polling_interval=5.0,
        )
        args = SimpleNamespace(watch=None, exclude=None, interval=None,
                               baseline=None, log_dir=None)
        merged = merge_cli_overrides(config, args)
        assert merged.monitored_paths == ["/var/www"]
        assert merged.exclude_patterns == ["*.log"]
        assert merged.polling_interval == 5.0

    def test_baseline_override(self):
        config = FIMConfig(baseline_file="default.txt")
        args = SimpleNamespace(watch=None, exclude=None, interval=None,
                               baseline="custom.txt", log_dir=None)
        merged = merge_cli_overrides(config, args)
        assert merged.baseline_file == "custom.txt"

    def test_critical_patterns_not_overridable(self):
        """Critical patterns come from config only, not CLI."""
        config = FIMConfig(critical_patterns=["*.conf", "*.env"])
        args = SimpleNamespace(watch=None, exclude=None, interval=None,
                               baseline=None, log_dir=None)
        merged = merge_cli_overrides(config, args)
        assert merged.critical_patterns == ["*.conf", "*.env"]
