# File Integrity Monitor (FIM) 🛡️

A lightweight, Python-based cybersecurity tool that monitors file integrity in real-time. It calculates SHA-256 hashes of files to create a baseline and alerts the user if any file is modified, deleted, or created.

##  Features
- **SHA-256 Hashing:** Uses secure hashing algorithms to verify file integrity.
- **Baseline Creation:** Scans a target directory to create a "known-good" state.
- **Real-Time Monitoring:** Continuously checks for changes against the baseline.
- **Instant Alerts:** Notifies the user immediately upon detection of:
  - File Modifications 📝
  - New File Creations 📄
  - File Deletions 🗑️

##  Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/sedat4ras/hash-based-change-detector.git](https://github.com/sedat4ras/hash-based-change-detector.git)
   cd hash-based-change-detector

   2. Create a folder to moonitor:
     mkdir monitored_files

Usage: python main.py

Step 1: Setup (Create Baseline)
Select Option 1 from the menu. The tool will scan the monitored_files folder and generate a baseline.txt file containing the initial file hashes.

Step 2: Defense (Start Monitoring)
Select Option 2 to begin the monitoring loop. The tool will check the files every second.

Exp Alert:

[!!! ALERT !!!] FILE CHANGED: monitored_files/passwords.txt
   Old Hash: a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e
   New Hash: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

   Disclaimer
This tool is developed for educational purposes and internal security testing.

Developed by sedat4ras

