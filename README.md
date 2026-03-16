# Hash-Based Change Detector

> A real-time file integrity monitoring (FIM) tool that uses SHA-256 hashing to detect unauthorized modifications, creations, and deletions — with forensic audit trail, rule-based filtering, and severity classification.

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![SHA-256](https://img.shields.io/badge/Hash-SHA--256-green?style=flat-square)]()
[![Tests](https://img.shields.io/badge/Tests-69_passed-brightgreen?style=flat-square)]()
[![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)]()

---

## Overview

File Integrity Monitoring is a core security control recommended by frameworks like PCI DSS and NIST. This tool implements FIM from scratch — it creates a cryptographic baseline of a directory's "known-good" state, then continuously monitors for deviations that could indicate unauthorized access, malware, or configuration tampering.

Every event is logged to structured JSON for forensic analysis and SIEM integration.

## How It Works

```
┌───────────────────────────────────────────────────────────────────────┐
│                      FILE INTEGRITY MONITOR v2.0                       │
├───────────────┬───────────────────────────────────────────────────────┤
│               │                                                       │
│   SETUP       │         MONITORING PIPELINE                           │
│               │                                                       │
│   Scan Dirs   │    ┌── Filter Engine ──┐                              │
│       │       │    │  Exclude: *.log   │                              │
│       ▼       │    │  Exclude: *.tmp   │                              │
│   SHA-256     │    └────────┬──────────┘                              │
│   Baseline    │             ▼                                         │
│       │       │    ┌── Compare Against Baseline ──────────────┐       │
│       ▼       │    │  Hash Match    → No Action               │       │
│   baseline    │    │  Hash Mismatch → MODIFIED Alert + Log    │       │
│   .txt        │    │  New File      → CREATED Alert  + Log    │       │
│               │    │  Missing File  → DELETED Alert  + Log    │       │
│               │    └──────────────────────────────────────────┘       │
│               │             ▼                                         │
│               │    ┌── Severity Classification ───────────────┐       │
│               │    │  *.conf, *.env, *.pem → CRITICAL (red)   │       │
│               │    │  Other files          → NORMAL            │       │
│               │    └──────────────────────────────────────────┘       │
│               │             ▼                                         │
│               │    JSON Audit Trail: logs/events_YYYY-MM-DD.json      │
└───────────────┴───────────────────────────────────────────────────────┘
```

## Features

| Feature | Description |
|---------|-------------|
| **SHA-256 Hashing** | Cryptographically secure file integrity verification with 4KB chunked reads |
| **Three-Event Detection** | Modifications, creations, and deletions detected in real time |
| **Forensic Audit Trail** | Every event logged to structured JSON with timestamps, hashes, and file sizes |
| **YAML Configuration** | Monitored paths, exclusion patterns, critical file patterns, polling interval |
| **Severity Classification** | CRITICAL alerts (red) for sensitive files (*.conf, *.env, *.pem, *passwd*) |
| **Glob-Based Filtering** | Exclude noise files (*.log, *.tmp, __pycache__/) from monitoring |
| **Multi-Directory Support** | Monitor multiple directories from a single config |
| **CLI + Legacy Menu** | Argparse subcommands with backward-compatible interactive menu |
| **Event Reports** | `--report` command for forensic summary of all recorded events |

## Quick Start

```bash
git clone https://github.com/sedat4ras/hash-based-change-detector.git
cd hash-based-change-detector

pip install -r requirements.txt

# Create baseline
python main.py setup

# Start monitoring
python main.py monitor

# View forensic event report
python main.py report

# Or use the interactive legacy menu
python main.py
```

## CLI Usage

```bash
# Basic usage with defaults (monitors monitored_files/)
python main.py setup
python main.py monitor

# Monitor a custom directory with exclusions
python main.py monitor --watch /etc/nginx --exclude "*.log" --interval 10

# Use a custom config file
python main.py monitor --config /etc/fim/production.yml

# Setup baseline for specific directory
python main.py setup --watch /var/www

# View forensic report
python main.py report
python main.py report --log-dir /var/log/fim
```

## Configuration

Create `config.yml` to customize monitoring behavior:

```yaml
# Directories to monitor
monitored_paths:
  - monitored_files
  - /etc/nginx
  - /var/www

# Exclude noisy files
exclude_patterns:
  - "*.log"
  - "*.tmp"
  - "*.swp"
  - "__pycache__/*"

# CRITICAL severity for sensitive files
critical_patterns:
  - "*.conf"
  - "*.env"
  - "*.pem"
  - "*.key"
  - "*passwd*"
  - "*shadow*"

# Scan interval in seconds
polling_interval: 5
```

CLI arguments override config values when provided.

## Event Log Format

Events are stored in `logs/events_YYYY-MM-DD.json`:

```json
[
  {
    "timestamp": "2026-03-16T14:23:01.456789+00:00",
    "event_type": "modified",
    "file_path": "monitored_files/passwords.txt",
    "old_hash": "fef24a2ef5f362f...",
    "new_hash": "a3c1b8e9d4f276a...",
    "file_size": 2048,
    "severity": "NORMAL"
  }
]
```

## Project Structure

```
hash-based-change-detector/
├── main.py                    # CLI entry point (argparse + legacy menu)
├── config.yml                 # YAML configuration
├── requirements.txt           # PyYAML>=6.0
├── fim/
│   ├── __init__.py            # Package init, version
│   ├── hasher.py              # SHA-256 file hashing
│   ├── event_logger.py        # JSON audit trail logger
│   ├── baseline.py            # Baseline create/load operations
│   ├── monitor.py             # Core monitoring loop + deletion detection
│   ├── reporter.py            # Event summary report generator
│   ├── config_loader.py       # YAML config + CLI override merging
│   └── filter_engine.py       # Glob exclusion + severity classification
├── tests/                     # 69 unit tests
├── monitored_files/           # Default monitored directory
└── LICENSE
```

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Changelog

### v2.0.0
- YAML config file support (monitored paths, exclusions, critical patterns, interval)
- Severity classification: CRITICAL files get red alerts
- Glob-based exclusion engine (*.log, *.tmp, __pycache__/)
- Multi-directory monitoring from single config
- CLI overrides: --watch, --exclude, --interval, --config
- Configurable polling interval (default: 5s)
- 36 new tests (69 total)

### v1.1.0
- Modular architecture: refactored into `fim/` package
- Forensic audit trail: structured JSON event logging
- File deletion detection (set-difference algorithm)
- Event report command (`python main.py report`)
- Argparse CLI with `setup`, `monitor`, `report` subcommands
- Backward-compatible legacy interactive menu
- 33 unit tests

### v1.0.0
- Basic SHA-256 file integrity monitor
- Baseline creation and continuous monitoring
- Modification and new file detection

## Disclaimer

This tool is developed for **educational purposes and authorized security testing only**. Always ensure you have explicit permission before monitoring systems or files that do not belong to you.

## Contact

GitHub: [sedat4ras](https://github.com/sedat4ras) | Email: sudo@sedataras.com
