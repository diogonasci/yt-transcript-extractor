"""Tests for utils module."""

from study.core.utils import sanitize_filename


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
        assert sanitize_filename("Video em Portugues") == "Video em Portugues"
