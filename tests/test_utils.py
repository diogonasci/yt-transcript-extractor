"""Tests for utils module."""

from pathlib import Path

from yt_transcript_extractor.utils import build_output_path, sanitize_filename


class TestSanitizeFilename:
    def test_removes_invalid_chars(self):
        assert sanitize_filename('test/file:name*"foo') == "test_file_name_foo"

    def test_collapses_underscores(self):
        assert sanitize_filename("a///b") == "a_b"

    def test_strips_trailing_dots_and_spaces(self):
        assert sanitize_filename("test...") == "test"
        assert sanitize_filename("  test  ") == "test"

    def test_truncates_long_names(self):
        long_name = "a" * 300
        result = sanitize_filename(long_name)
        assert len(result) <= 200

    def test_empty_string_returns_untitled(self):
        assert sanitize_filename("") == "untitled"
        assert sanitize_filename("...") == "untitled"

    def test_normal_name_unchanged(self):
        assert sanitize_filename("My Great Video") == "My Great Video"

    def test_unicode_preserved(self):
        assert sanitize_filename("Vídeo em Português") == "Vídeo em Português"


class TestBuildOutputPath:
    def test_correct_structure(self, tmp_path: Path):
        path = build_output_path(tmp_path, "My Channel", "20240101", "Video Title")
        assert path == tmp_path / "My Channel" / "20240101 - Video Title.json"

    def test_creates_directories(self, tmp_path: Path):
        output = tmp_path / "output"
        path = build_output_path(output, "Channel", "20240101", "Title")
        assert path.parent.exists()

    def test_sanitizes_channel_and_title(self, tmp_path: Path):
        path = build_output_path(tmp_path, "Ch/annel", "20240101", "Ti:tle")
        assert "Ch_annel" in str(path)
        assert "Ti_tle" in str(path)
