"""Shared test fixtures and sample data."""

import json
import pytest
from pathlib import Path


SAMPLE_JSON3 = {
    "events": [
        # Should be skipped: only newline
        {"tStartMs": 0, "dDurationMs": 5000, "segs": [{"utf8": "\n"}]},
        # Valid segment with multiple segs
        {
            "tStartMs": 5000,
            "dDurationMs": 3000,
            "segs": [{"utf8": "Hello "}, {"utf8": "world"}],
        },
        # Valid single segment
        {
            "tStartMs": 8000,
            "dDurationMs": 2500,
            "segs": [{"utf8": "Second line"}],
        },
        # Should be skipped: no segs key
        {"tStartMs": 10500, "dDurationMs": 1000},
        # Should be skipped: empty segs
        {"tStartMs": 12000, "dDurationMs": 500, "segs": []},
    ],
}

SAMPLE_VTT = """\
WEBVTT
Kind: captions
Language: en

00:00:05.000 --> 00:00:08.000
Hello world

00:00:08.000 --> 00:00:10.500
Second line

00:00:10.500 --> 00:00:12.000
<c>Third</c> <c>with tags</c>
"""

SAMPLE_SRT = """\
1
00:00:05,000 --> 00:00:08,000
Hello world

2
00:00:08,000 --> 00:00:10,500
Second line

3
00:00:10,500 --> 00:00:12,000
Third line
"""

SAMPLE_INFO_DICT = {
    "id": "abc123",
    "title": "Test Video Title",
    "channel": "Test Channel",
    "uploader": "Test Uploader",
    "upload_date": "20240615",
    "webpage_url": "https://www.youtube.com/watch?v=abc123",
    "requested_subtitles": {},
}


@pytest.fixture
def json3_file(tmp_path: Path) -> Path:
    filepath = tmp_path / "test.json3"
    filepath.write_text(json.dumps(SAMPLE_JSON3), encoding="utf-8")
    return filepath


@pytest.fixture
def vtt_file(tmp_path: Path) -> Path:
    filepath = tmp_path / "test.vtt"
    filepath.write_text(SAMPLE_VTT, encoding="utf-8")
    return filepath


@pytest.fixture
def srt_file(tmp_path: Path) -> Path:
    filepath = tmp_path / "test.srt"
    filepath.write_text(SAMPLE_SRT, encoding="utf-8")
    return filepath
