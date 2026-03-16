"""File hashing module — SHA-256 integrity verification."""

from __future__ import annotations

import hashlib


def calculate_hash(
    file_path: str,
    algorithm: str = "sha256",
    chunk_size: int = 4096,
) -> str | None:
    """Calculate the cryptographic hash of a file.

    Reads the file in chunks to keep memory usage constant
    regardless of file size.

    Args:
        file_path: Path to the file to hash.
        algorithm: Hash algorithm name (default: sha256).
        chunk_size: Read buffer size in bytes (default: 4096).

    Returns:
        Hex digest string, or None if the file cannot be read.
    """
    hash_obj = hashlib.new(algorithm)
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(chunk_size), b""):
                hash_obj.update(byte_block)
        return hash_obj.hexdigest()
    except (FileNotFoundError, PermissionError, OSError):
        return None
