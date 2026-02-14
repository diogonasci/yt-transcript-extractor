"""Tests for parser module."""

import json
from pathlib import Path

from yt_transcript_extractor.config import TranscriptResult, TranscriptSegment
from yt_transcript_extractor.parser import (
    parse_json3,
    parse_srt,
    parse_subtitle_file,
    parse_vtt,
    result_to_dict,
    write_result,
)


class TestParseJson3:
    def test_parses_valid_segments(self, json3_file: Path):
        segments = parse_json3(json3_file)
        assert len(segments) == 2
        assert segments[0].text == "Hello world"
        assert segments[0].start == 5.0
        assert segments[0].duration == 3.0
        assert segments[1].text == "Second line"
        assert segments[1].start == 8.0
        assert segments[1].duration == 2.5

    def test_skips_newline_only(self, json3_file: Path):
        segments = parse_json3(json3_file)
        texts = [s.text for s in segments]
        assert "\n" not in texts

    def test_empty_events(self, tmp_path: Path):
        filepath = tmp_path / "empty.json3"
        filepath.write_text(json.dumps({"events": []}), encoding="utf-8")
        assert parse_json3(filepath) == []


class TestParseVtt:
    def test_parses_valid_cues(self, vtt_file: Path):
        segments = parse_vtt(vtt_file)
        assert len(segments) == 3
        assert segments[0].text == "Hello world"
        assert segments[0].start == 5.0
        assert segments[0].duration == 3.0

    def test_strips_vtt_tags(self, vtt_file: Path):
        segments = parse_vtt(vtt_file)
        assert segments[2].text == "Third with tags"


class TestParseSrt:
    def test_parses_valid_blocks(self, srt_file: Path):
        segments = parse_srt(srt_file)
        assert len(segments) == 3
        assert segments[0].text == "Hello world"
        assert segments[0].start == 5.0
        assert segments[0].duration == 3.0
        assert segments[2].text == "Third line"


class TestParseSubtitleFile:
    def test_dispatches_json3(self, json3_file: Path):
        segments = parse_subtitle_file(json3_file, "json3")
        assert len(segments) == 2

    def test_dispatches_vtt(self, vtt_file: Path):
        segments = parse_subtitle_file(vtt_file, "vtt")
        assert len(segments) == 3

    def test_dispatches_srt(self, srt_file: Path):
        segments = parse_subtitle_file(srt_file, "srt")
        assert len(segments) == 3

    def test_invalid_format_raises(self, json3_file: Path):
        import pytest

        with pytest.raises(ValueError, match="Unsupported"):
            parse_subtitle_file(json3_file, "unknown")


class TestWriteResult:
    def test_writes_valid_json(self, tmp_path: Path):
        result = TranscriptResult(
            id="abc",
            title="Test",
            channel="Channel",
            upload_date="20240101",
            webpage_url="https://example.com",
            transcript=[TranscriptSegment(text="Hello", start=0.0, duration=1.0)],
        )
        output = tmp_path / "output.json"
        write_result(result, output)

        data = json.loads(output.read_text(encoding="utf-8"))
        assert data["id"] == "abc"
        assert data["title"] == "Test"
        assert len(data["transcript"]) == 1
        assert data["transcript"][0]["text"] == "Hello"

    def test_result_to_dict(self):
        result = TranscriptResult(
            id="abc",
            title="Test",
            channel="Ch",
            upload_date="20240101",
            webpage_url="https://example.com",
            transcript=[],
        )
        d = result_to_dict(result)
        assert isinstance(d, dict)
        assert d["id"] == "abc"
        assert d["transcript"] == []
