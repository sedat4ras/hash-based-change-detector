"""Configuration loader — YAML config + CLI override merging."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

DEFAULT_CONFIG_PATH = "config.yml"


@dataclass
class FIMConfig:
    """Configuration for the File Integrity Monitor."""

    monitored_paths: list[str] = field(
        default_factory=lambda: ["monitored_files"]
    )
    exclude_patterns: list[str] = field(default_factory=list)
    critical_patterns: list[str] = field(default_factory=list)
    polling_interval: float = 5.0
    baseline_file: str = "baseline.txt"
    log_dir: str = "logs"


def load_config(config_path: str = DEFAULT_CONFIG_PATH) -> FIMConfig:
    """Load configuration from a YAML file.

    If the file does not exist, returns defaults.
    PyYAML import is deferred so the tool works without it
    when no config file is present.

    Args:
        config_path: Path to the YAML config file.

    Returns:
        FIMConfig instance.
    """
    if not os.path.exists(config_path):
        return FIMConfig()

    import yaml

    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    return FIMConfig(
        monitored_paths=raw.get("monitored_paths", ["monitored_files"]),
        exclude_patterns=raw.get("exclude_patterns", []),
        critical_patterns=raw.get("critical_patterns", []),
        polling_interval=float(raw.get("polling_interval", 5.0)),
        baseline_file=raw.get("baseline_file", "baseline.txt"),
        log_dir=raw.get("log_dir", "logs"),
    )


def merge_cli_overrides(config: FIMConfig, args) -> FIMConfig:
    """Apply CLI argument overrides to a loaded config.

    Args:
        config: Base FIMConfig from YAML.
        args: argparse.Namespace with optional overrides.

    Returns:
        New FIMConfig with overrides applied.
    """
    monitored_paths = config.monitored_paths
    if hasattr(args, "watch") and args.watch:
        monitored_paths = [args.watch]

    exclude_patterns = list(config.exclude_patterns)
    if hasattr(args, "exclude") and args.exclude:
        exclude_patterns.append(args.exclude)

    polling_interval = config.polling_interval
    if hasattr(args, "interval") and args.interval is not None:
        polling_interval = args.interval

    baseline_file = config.baseline_file
    if hasattr(args, "baseline") and args.baseline:
        baseline_file = args.baseline

    log_dir = config.log_dir
    if hasattr(args, "log_dir") and args.log_dir:
        log_dir = args.log_dir

    return FIMConfig(
        monitored_paths=monitored_paths,
        exclude_patterns=exclude_patterns,
        critical_patterns=config.critical_patterns,
        polling_interval=polling_interval,
        baseline_file=baseline_file,
        log_dir=log_dir,
    )
