"""Tests for transcript parser."""

import json
from pathlib import Path

import pytest

from study.core.models import TranscriptSegment, TranscriptResult
from study.transcript.parser import (
    parse_json3,
    parse_vtt,
    parse_srt,
    parse_subtitle_file,
    result_to_dict,
)


class TestParseJson3:
    def test_parses_valid_segments(self, json3_file):
        segments = parse_json3(json3_file)
        assert len(segments) == 2
        assert segments[0].text == "Hello world"
        assert segments[0].start == 5.0
        assert segments[0].duration == 3.0

    def test_skips_empty_and_newline(self, json3_file):
        segments = parse_json3(json3_file)
        texts = [s.text for s in segments]
        assert "\n" not in texts

    def test_concatenates_multiple_segs(self, json3_file):
        segments = parse_json3(json3_file)
        assert segments[0].text == "Hello world"

    def test_second_segment(self, json3_file):
        segments = parse_json3(json3_file)
        assert segments[1].text == "Second line"
        assert segments[1].start == 8.0
        assert segments[1].duration == 2.5


class TestParseVtt:
    def test_parses_valid_segments(self, vtt_file):
        segments = parse_vtt(vtt_file)
        assert len(segments) == 3
        assert segments[0].text == "Hello world"

    def test_strips_tags(self, vtt_file):
        segments = parse_vtt(vtt_file)
        assert "<c>" not in segments[2].text
        assert segments[2].text == "Third with tags"

    def test_timestamps(self, vtt_file):
        segments = parse_vtt(vtt_file)
        assert segments[0].start == 5.0
        assert segments[0].duration == 3.0


class TestParseSrt:
    def test_parses_valid_segments(self, srt_file):
        segments = parse_srt(srt_file)
        assert len(segments) == 3
        assert segments[0].text == "Hello world"

    def test_timestamps(self, srt_file):
        segments = parse_srt(srt_file)
        assert segments[0].start == 5.0
        assert segments[0].duration == 3.0
        assert segments[2].text == "Third line"


class TestParseSubtitleFile:
    def test_dispatches_json3(self, json3_file):
        segments = parse_subtitle_file(json3_file, "json3")
        assert len(segments) == 2

    def test_dispatches_vtt(self, vtt_file):
        segments = parse_subtitle_file(vtt_file, "vtt")
        assert len(segments) == 3

    def test_dispatches_srt(self, srt_file):
        segments = parse_subtitle_file(srt_file, "srt")
        assert len(segments) == 3

    def test_unsupported_format_raises(self, json3_file):
        with pytest.raises(ValueError, match="Unsupported subtitle format"):
            parse_subtitle_file(json3_file, "ass")


class TestResultToDict:
    def test_includes_full_text(self):
        result = TranscriptResult(
            id="vid1",
            title="Test",
            channel="Chan",
            upload_date="20240101",
            webpage_url="https://example.com",
            transcript=[
                TranscriptSegment(text="Hello", start=0.0, duration=1.0),
                TranscriptSegment(text="world", start=1.0, duration=1.0),
            ],
        )
        d = result_to_dict(result)
        assert d["full_text"] == "Hello world"
        assert d["id"] == "vid1"
        assert len(d["transcript"]) == 2
