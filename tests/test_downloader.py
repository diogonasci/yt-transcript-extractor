"""Tests for downloader module (with mocked yt-dlp)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from yt_transcript_extractor.config import ExtractorConfig
from yt_transcript_extractor.downloader import (
    _flatten_entries,
    _is_archived,
    _process_entry,
    _record_in_archive,
)

from .conftest import SAMPLE_JSON3


class TestFlattenEntries:
    def test_single_video(self):
        info = {"id": "abc", "title": "Test"}
        assert _flatten_entries(info) == [info]

    def test_playlist(self):
        info = {
            "entries": [
                {"id": "a", "title": "A"},
                {"id": "b", "title": "B"},
            ]
        }
        result = _flatten_entries(info)
        assert len(result) == 2
        assert result[0]["id"] == "a"

    def test_nested_entries(self):
        info = {
            "entries": [
                {
                    "entries": [
                        {"id": "a"},
                        {"id": "b"},
                    ]
                },
                {"id": "c"},
            ]
        }
        result = _flatten_entries(info)
        assert len(result) == 3

    def test_none_entries_skipped(self):
        info = {"entries": [None, {"id": "a"}, None]}
        result = _flatten_entries(info)
        assert len(result) == 1

    def test_none_input(self):
        assert _flatten_entries(None) == []


class TestProcessEntry:
    def test_processes_valid_entry(self, tmp_path: Path):
        # Write a subtitle file
        sub_path = tmp_path / "abc123.en.json3"
        sub_path.write_text(json.dumps(SAMPLE_JSON3), encoding="utf-8")

        entry = {
            "id": "abc123",
            "title": "Test Video",
            "channel": "Test Channel",
            "upload_date": "20240615",
            "webpage_url": "https://www.youtube.com/watch?v=abc123",
            "requested_subtitles": {
                "en": {"filepath": str(sub_path), "ext": "json3"}
            },
        }

        config = ExtractorConfig(
            output_dir=tmp_path / "output",
            archive_file=tmp_path / "archive.txt",
        )
        result = _process_entry(entry, config, tmp_path)

        assert result is not None
        assert result.id == "abc123"
        assert result.title == "Test Video"
        assert result.channel == "Test Channel"
        assert len(result.transcript) == 2
        assert result.transcript[0].text == "Hello world"

        # Verify file was written
        output_file = tmp_path / "output" / "Test Channel" / "20240615 - Test Video.json"
        assert output_file.exists()

    def test_returns_none_when_no_subtitles(self, tmp_path: Path):
        entry = {
            "id": "abc123",
            "title": "No Subs Video",
            "channel": "Channel",
            "upload_date": "20240101",
            "webpage_url": "https://example.com",
            "requested_subtitles": {},
        }

        config = ExtractorConfig(
            output_dir=tmp_path / "output",
            archive_file=tmp_path / "archive.txt",
        )
        result = _process_entry(entry, config, tmp_path)
        assert result is None

    def test_fallback_file_discovery(self, tmp_path: Path):
        """When requested_subtitles has no filepath, scan temp dir."""
        sub_path = tmp_path / "abc123.en.json3"
        sub_path.write_text(json.dumps(SAMPLE_JSON3), encoding="utf-8")

        entry = {
            "id": "abc123",
            "title": "Fallback Test",
            "channel": "Channel",
            "upload_date": "20240101",
            "webpage_url": "https://example.com",
            "requested_subtitles": None,
        }

        config = ExtractorConfig(
            output_dir=tmp_path / "output",
            archive_file=tmp_path / "archive.txt",
        )
        result = _process_entry(entry, config, tmp_path)

        assert result is not None
        assert len(result.transcript) == 2


class TestArchiveDeduplication:
    def test_record_creates_archive_file(self, tmp_path: Path):
        archive = tmp_path / "archive.txt"
        entry = {"id": "abc123", "extractor": "youtube"}
        _record_in_archive(archive, entry)
        assert archive.exists()
        assert "youtube abc123" in archive.read_text()

    def test_record_does_not_duplicate(self, tmp_path: Path):
        archive = tmp_path / "archive.txt"
        entry = {"id": "abc123", "extractor": "youtube"}
        _record_in_archive(archive, entry)
        _record_in_archive(archive, entry)
        lines = archive.read_text().strip().splitlines()
        assert len(lines) == 1

    def test_record_appends_different_ids(self, tmp_path: Path):
        archive = tmp_path / "archive.txt"
        _record_in_archive(archive, {"id": "aaa", "extractor": "youtube"})
        _record_in_archive(archive, {"id": "bbb", "extractor": "youtube"})
        lines = archive.read_text().strip().splitlines()
        assert len(lines) == 2

    def test_is_archived_returns_true(self, tmp_path: Path):
        archive = tmp_path / "archive.txt"
        archive.write_text("youtube abc123\n")
        assert _is_archived(archive, {"id": "abc123"}) is True

    def test_is_archived_returns_false(self, tmp_path: Path):
        archive = tmp_path / "archive.txt"
        archive.write_text("youtube abc123\n")
        assert _is_archived(archive, {"id": "xyz789"}) is False

    def test_is_archived_no_file(self, tmp_path: Path):
        archive = tmp_path / "archive.txt"
        assert _is_archived(archive, {"id": "abc123"}) is False

    def test_process_entry_skips_archived(self, tmp_path: Path):
        archive = tmp_path / "archive.txt"
        archive.write_text("youtube abc123\n")

        sub_path = tmp_path / "abc123.en.json3"
        sub_path.write_text(json.dumps(SAMPLE_JSON3), encoding="utf-8")

        entry = {
            "id": "abc123",
            "title": "Already Done",
            "channel": "Channel",
            "upload_date": "20240101",
            "webpage_url": "https://example.com",
            "requested_subtitles": {
                "en": {"filepath": str(sub_path), "ext": "json3"}
            },
        }

        config = ExtractorConfig(
            output_dir=tmp_path / "output",
            archive_file=archive,
        )
        result = _process_entry(entry, config, tmp_path)
        assert result is None

    def test_process_entry_records_after_success(self, tmp_path: Path):
        archive = tmp_path / "archive.txt"
        sub_path = tmp_path / "new123.en.json3"
        sub_path.write_text(json.dumps(SAMPLE_JSON3), encoding="utf-8")

        entry = {
            "id": "new123",
            "title": "New Video",
            "channel": "Channel",
            "upload_date": "20240101",
            "webpage_url": "https://example.com",
            "extractor": "youtube",
            "requested_subtitles": {
                "en": {"filepath": str(sub_path), "ext": "json3"}
            },
        }

        config = ExtractorConfig(
            output_dir=tmp_path / "output",
            archive_file=archive,
        )
        result = _process_entry(entry, config, tmp_path)
        assert result is not None
        assert archive.exists()
        assert "youtube new123" in archive.read_text()
