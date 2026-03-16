"""Tests for the hasher module."""

import hashlib

from fim.hasher import calculate_hash


class TestCalculateHash:
    def test_known_content(self, tmp_path):
        f = tmp_path / "test.txt"
        content = b"Hello World"
        f.write_bytes(content)
        expected = hashlib.sha256(content).hexdigest()
        assert calculate_hash(str(f)) == expected

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_bytes(b"")
        expected = hashlib.sha256(b"").hexdigest()
        assert calculate_hash(str(f)) == expected

    def test_nonexistent_file(self):
        assert calculate_hash("/nonexistent/path/file.txt") is None

    def test_binary_file(self, tmp_path):
        f = tmp_path / "binary.bin"
        data = bytes(range(256))
        f.write_bytes(data)
        expected = hashlib.sha256(data).hexdigest()
        assert calculate_hash(str(f)) == expected

    def test_large_file_chunked(self, tmp_path):
        """File larger than chunk size should hash correctly."""
        f = tmp_path / "large.bin"
        data = b"A" * 10000  # Larger than 4096 chunk
        f.write_bytes(data)
        expected = hashlib.sha256(data).hexdigest()
        assert calculate_hash(str(f)) == expected

    def test_different_content_different_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("content A")
        f2.write_text("content B")
        assert calculate_hash(str(f1)) != calculate_hash(str(f2))

    def test_same_content_same_hash(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("identical")
        f2.write_text("identical")
        assert calculate_hash(str(f1)) == calculate_hash(str(f2))

    def test_returns_hex_string(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("data")
        result = calculate_hash(str(f))
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 hex digest length
        assert all(c in "0123456789abcdef" for c in result)
