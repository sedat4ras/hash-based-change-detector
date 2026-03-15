# Hash-Based Change Detector

> A real-time file integrity monitoring (FIM) tool that uses SHA-256 hashing to detect unauthorized modifications, creations, and deletions in monitored directories.

[![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![SHA-256](https://img.shields.io/badge/Hash-SHA--256-green?style=flat-square)]()
[![Purpose](https://img.shields.io/badge/Purpose-File_Integrity_Monitoring-orange?style=flat-square)]()
[![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)]()

---

## Overview

File Integrity Monitoring is a core security control recommended by frameworks like PCI DSS and NIST. This tool implements FIM from scratch — it creates a cryptographic baseline of a directory's "known-good" state, then continuously monitors for deviations that could indicate unauthorized access, malware, or configuration tampering.

## How It Works

```
┌──────────────────────────────────────────────────────────────────┐
│                      FILE INTEGRITY MONITOR                      │
├──────────────────────┬───────────────────────────────────────────┤
│                      │                                           │
│   BASELINE MODE      │         MONITORING MODE                   │
│   (Option 1)         │         (Option 2)                        │
│                      │                                           │
│   Scan Directory     │    ┌─── Compare Against Baseline ───┐    │
│        │             │    │                                 │    │
│        ▼             │    │  Hash Match    → No Action      │    │
│   Calculate SHA-256  │    │  Hash Mismatch → MODIFIED Alert │    │
│   for each file      │    │  New File      → CREATED Alert  │    │
│        │             │    │  Missing File  → DELETED Alert  │    │
│        ▼             │    │                                 │    │
│   Save baseline.txt  │    └─────── Loop (every 1s) ────────┘    │
│                      │                                           │
└──────────────────────┴───────────────────────────────────────────┘
```

## Detection Capabilities

| Event | Detection Method | Alert Level |
|-------|-----------------|-------------|
| **File Modified** | SHA-256 hash mismatch against baseline | `[!!! ALERT !!!]` |
| **File Created** | New file not present in baseline | `[!!! ALERT !!!]` |
| **File Deleted** | Baseline entry with no matching file | `[!!! ALERT !!!]` |

## Quick Start

```bash
git clone https://github.com/sedat4ras/hash-based-change-detector.git
cd hash-based-change-detector

# Create a directory to monitor
mkdir monitored_files
echo "sensitive data" > monitored_files/passwords.txt
```

### Step 1 — Create Baseline

```bash
python3 main.py
# Select Option 1
```

This scans `monitored_files/` and generates `baseline.txt` containing the SHA-256 hash of every file.

### Step 2 — Start Monitoring

```bash
python3 main.py
# Select Option 2
```

The tool enters a continuous monitoring loop, scanning every second for changes.

### Step 3 — Test Detection

In a **second terminal**, simulate an unauthorized change:

```bash
echo "Unauthorized change" > monitored_files/passwords.txt
```

The monitor will immediately display:

```
[!!! ALERT !!!] FILE CHANGED: monitored_files/passwords.txt
```

![Alert Message](./alert-message.png)

## Technical Details

- **Hash Algorithm:** SHA-256 (cryptographically secure, collision-resistant)
- **Scan Interval:** 1 second continuous loop
- **Baseline Storage:** Plain-text file mapping `filepath → hash`
- **Dependencies:** Zero — uses only Python standard library (`hashlib`, `os`, `time`)

## Troubleshooting

| Issue | Solution |
|-------|---------|
| Permission Denied (macOS/Linux) | `sudo chown -R $(whoami) .` |
| No Alert Triggered | Ensure monitoring mode (Option 2) is active and files are inside `monitored_files/` |
| Baseline Missing | Run Option 1 before starting the monitor |

## Disclaimer

This tool is developed for **educational purposes and internal security testing only**. Always ensure you have explicit permission before monitoring systems or files that do not belong to you.

## Contact

GitHub: [sedat4ras](https://github.com/sedat4ras) | Email: sudo@sedataras.com
