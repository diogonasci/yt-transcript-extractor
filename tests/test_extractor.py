"""Tests for transcript extractor with mocked yt-dlp."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from study.core.config import Settings
from study.core.models import TranscriptResult
from study.transcript.extractor import (
    extract_transcripts,
    _flatten_entries,
    _detect_format,
    _find_subtitle_file,
    _process_entry,
)

SAMPLE_JSON3 = {
    "events": [
        {"tStartMs": 0, "dDurationMs": 5000, "segs": [{"utf8": "\n"}]},
        {
            "tStartMs": 5000,
            "dDurationMs": 3000,
            "segs": [{"utf8": "Hello "}, {"utf8": "world"}],
        },
        {
            "tStartMs": 8000,
            "dDurationMs": 2500,
            "segs": [{"utf8": "Second line"}],
        },
        {"tStartMs": 10500, "dDurationMs": 1000},
        {"tStartMs": 12000, "dDurationMs": 500, "segs": []},
    ],
}


@pytest.fixture
def settings(tmp_path):
    return Settings(
        vault_path=tmp_path,
        claude_backend="api",
        anthropic_api_key="test-key",
        claude_model="test-model",
        transcript_lang="en",
        subtitle_format="json3",
        content_lang="pt-BR",
        data_dir=tmp_path / "data",
        archive_file=tmp_path / "data" / "archive.txt",
        verbose=False,
    )


class TestFlattenEntries:
    def test_single_video(self):
        info = {"id": "abc123", "title": "Test"}
        assert _flatten_entries(info) == [info]

    def test_playlist(self):
        info = {
            "entries": [
                {"id": "vid1", "title": "Video 1"},
                {"id": "vid2", "title": "Video 2"},
            ]
        }
        result = _flatten_entries(info)
        assert len(result) == 2
        assert result[0]["id"] == "vid1"

    def test_nested_entries(self):
        info = {
            "entries": [
                {
                    "entries": [
                        {"id": "vid1"},
                        {"id": "vid2"},
                    ]
                }
            ]
        }
        result = _flatten_entries(info)
        assert len(result) == 2

    def test_none_entries_skipped(self):
        info = {"entries": [None, {"id": "vid1"}, None]}
        result = _flatten_entries(info)
        assert len(result) == 1

    def test_none_input(self):
        assert _flatten_entries(None) == []


class TestDetectFormat:
    def test_json3_extension(self, settings):
        assert _detect_format(Path("test.json3"), settings) == "json3"

    def test_vtt_extension(self, settings):
        assert _detect_format(Path("test.vtt"), settings) == "vtt"

    def test_srt_extension(self, settings):
        assert _detect_format(Path("test.srt"), settings) == "srt"

    def test_unknown_falls_back_to_config(self, settings):
        assert _detect_format(Path("test.txt"), settings) == "json3"


class TestFindSubtitleFile:
    def test_finds_from_requested_subtitles(self, settings, tmp_path):
        sub_file = tmp_path / "abc123.json3"
        sub_file.write_text("{}")
        entry = {
            "id": "abc123",
            "requested_subtitles": {
                "en": {"filepath": str(sub_file)}
            },
        }
        result = _find_subtitle_file(entry, settings, tmp_path)
        assert result == sub_file

    def test_finds_from_scan(self, settings, tmp_path):
        sub_file = tmp_path / "abc123.en.json3"
        sub_file.write_text("{}")
        entry = {"id": "abc123", "requested_subtitles": {}}
        result = _find_subtitle_file(entry, settings, tmp_path)
        assert result == sub_file

    def test_returns_none_when_not_found(self, settings, tmp_path):
        entry = {"id": "abc123", "requested_subtitles": {}}
        result = _find_subtitle_file(entry, settings, tmp_path)
        assert result is None


class TestProcessEntry:
    def test_processes_valid_entry(self, settings, tmp_path):
        sub_file = tmp_path / "abc123.json3"
        sub_file.write_text(json.dumps(SAMPLE_JSON3))
        entry = {
            "id": "abc123",
            "title": "Test Video",
            "channel": "Test Channel",
            "upload_date": "20240615",
            "webpage_url": "https://example.com",
            "requested_subtitles": {
                "en": {"filepath": str(sub_file)}
            },
        }
        result = _process_entry(entry, settings, tmp_path)
        assert result is not None
        assert isinstance(result, TranscriptResult)
        assert result.id == "abc123"
        assert result.title == "Test Video"
        assert len(result.transcript) == 2

    def test_returns_none_when_no_subtitle(self, settings, tmp_path):
        entry = {
            "id": "abc123",
            "title": "Test Video",
            "requested_subtitles": {},
        }
        result = _process_entry(entry, settings, tmp_path)
        assert result is None


class TestExtractTranscripts:
    @patch("study.transcript.extractor.yt_dlp.YoutubeDL")
    def test_extracts_from_url(self, mock_ydl_class, settings, tmp_path):
        sub_file = tmp_path / "abc123.json3"
        sub_file.write_text(json.dumps(SAMPLE_JSON3))

        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl_class.return_value.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.return_value = {
            "id": "abc123",
            "title": "Test Video",
            "channel": "Test Channel",
            "upload_date": "20240615",
            "webpage_url": "https://example.com",
            "requested_subtitles": {
                "en": {"filepath": str(sub_file)}
            },
        }

        results = extract_transcripts(["https://example.com"], settings)
        assert len(results) == 1
        assert results[0].id == "abc123"

    @patch("study.transcript.extractor.yt_dlp.YoutubeDL")
    def test_handles_extract_error(self, mock_ydl_class, settings):
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl_class.return_value.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.side_effect = Exception("Network error")

        results = extract_transcripts(["https://example.com"], settings)
        assert results == []

    @patch("study.transcript.extractor.yt_dlp.YoutubeDL")
    def test_handles_none_info(self, mock_ydl_class, settings):
        mock_ydl = MagicMock()
        mock_ydl_class.return_value.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl_class.return_value.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.return_value = None

        results = extract_transcripts(["https://example.com"], settings)
        assert results == []
