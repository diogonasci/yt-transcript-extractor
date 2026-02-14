"""Tests for CLI argument parsing."""

import pytest
from pathlib import Path

from yt_transcript_extractor.cli import build_parser
from yt_transcript_extractor.config import DEFAULT_ARCHIVE, DEFAULT_LANG, DEFAULT_OUTPUT_DIR


class TestBuildParser:
    def setup_method(self):
        self.parser = build_parser()

    def test_channel_mode(self):
        args = self.parser.parse_args(["channel", "https://youtube.com/@test"])
        assert args.mode == "channel"
        assert args.url == "https://youtube.com/@test"
        assert args.output == DEFAULT_OUTPUT_DIR
        assert args.lang == DEFAULT_LANG
        assert args.archive == DEFAULT_ARCHIVE
        assert args.subtitle_format == "json3"
        assert args.verbose is False

    def test_channel_with_after(self):
        args = self.parser.parse_args(
            ["channel", "https://youtube.com/@test", "--after", "20240101"]
        )
        assert args.after == "20240101"

    def test_playlist_mode_single(self):
        args = self.parser.parse_args(["playlist", "https://youtube.com/playlist?list=XYZ"])
        assert args.mode == "playlist"
        assert args.urls == ["https://youtube.com/playlist?list=XYZ"]

    def test_playlist_mode_multiple(self):
        args = self.parser.parse_args(["playlist", "url1", "url2", "url3"])
        assert args.urls == ["url1", "url2", "url3"]

    def test_list_mode(self):
        args = self.parser.parse_args(["list", "videos.txt"])
        assert args.mode == "list"
        assert args.file == Path("videos.txt")

    def test_custom_options(self):
        args = self.parser.parse_args([
            "channel", "https://youtube.com/@test",
            "--output", "/tmp/out",
            "--lang", "pt",
            "--archive", "done.txt",
            "--format", "srt",
            "--verbose",
        ])
        assert args.output == Path("/tmp/out")
        assert args.lang == "pt"
        assert args.archive == Path("done.txt")
        assert args.subtitle_format == "srt"
        assert args.verbose is True

    def test_no_mode_raises(self):
        with pytest.raises(SystemExit):
            self.parser.parse_args([])

    def test_invalid_format_raises(self):
        with pytest.raises(SystemExit):
            self.parser.parse_args(["channel", "url", "--format", "invalid"])
