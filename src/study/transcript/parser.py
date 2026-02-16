"""Subtitle file parsing (json3, vtt, srt) and serialization."""

import json
import re
from dataclasses import asdict
from pathlib import Path

from study.core.models import TranscriptResult, TranscriptSegment


def parse_subtitle_file(filepath: Path, fmt: str) -> list[TranscriptSegment]:
    """Parse a subtitle file into transcript segments."""
    parsers = {
        "json3": parse_json3,
        "vtt": parse_vtt,
        "srt": parse_srt,
    }
    parser = parsers.get(fmt)
    if parser is None:
        raise ValueError(f"Unsupported subtitle format: {fmt}")
    return parser(filepath)


def parse_json3(filepath: Path) -> list[TranscriptSegment]:
    """Parse YouTube json3 subtitle format."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    segments: list[TranscriptSegment] = []
    for event in data.get("events", []):
        segs = event.get("segs")
        if not segs:
            continue
        text = "".join(seg.get("utf8", "") for seg in segs).strip()
        if not text or text == "\n":
            continue

        start_ms = event.get("tStartMs", 0)
        duration_ms = event.get("dDurationMs", 0)

        segments.append(
            TranscriptSegment(
                text=text,
                start=round(start_ms / 1000.0, 3),
                duration=round(duration_ms / 1000.0, 3),
            )
        )
    return segments


def _parse_vtt_timestamp(ts: str) -> float:
    """Convert a VTT timestamp (HH:MM:SS.mmm or MM:SS.mmm) to seconds."""
    parts = ts.strip().split(":")
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    return 0.0


def parse_vtt(filepath: Path) -> list[TranscriptSegment]:
    """Parse WebVTT subtitle format."""
    content = filepath.read_text(encoding="utf-8")
    segments: list[TranscriptSegment] = []

    pattern = re.compile(
        r"(\d{1,2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}\.\d{3})[^\n]*\n((?:(?!\d{1,2}:\d{2}:\d{2}\.\d{3}\s*-->).+\n?)*)",
    )

    for match in pattern.finditer(content):
        start_ts, end_ts, text_block = match.group(1), match.group(2), match.group(3)
        text = re.sub(r"<[^>]+>", "", text_block).strip()
        if not text:
            continue

        start = _parse_vtt_timestamp(start_ts)
        end = _parse_vtt_timestamp(end_ts)
        duration = round(end - start, 3)

        segments.append(
            TranscriptSegment(
                text=text,
                start=round(start, 3),
                duration=duration,
            )
        )
    return segments


def _parse_srt_timestamp(ts: str) -> float:
    """Convert an SRT timestamp (HH:MM:SS,mmm) to seconds."""
    ts = ts.strip().replace(",", ".")
    parts = ts.split(":")
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    return 0.0


def parse_srt(filepath: Path) -> list[TranscriptSegment]:
    """Parse SRT subtitle format."""
    content = filepath.read_text(encoding="utf-8")
    segments: list[TranscriptSegment] = []

    pattern = re.compile(
        r"\d+\s*\n(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\s*\n((?:(?!\d+\s*\n\d{2}:\d{2}:\d{2}).+\n?)*)",
    )

    for match in pattern.finditer(content):
        start_ts, end_ts, text_block = match.group(1), match.group(2), match.group(3)
        text = text_block.strip()
        if not text:
            continue

        start = _parse_srt_timestamp(start_ts)
        end = _parse_srt_timestamp(end_ts)
        duration = round(end - start, 3)

        segments.append(
            TranscriptSegment(
                text=text,
                start=round(start, 3),
                duration=duration,
            )
        )
    return segments


def result_to_dict(result: TranscriptResult) -> dict:
    """Convert a TranscriptResult to a plain dict for serialization."""
    data = asdict(result)
    data["full_text"] = result.full_text
    return data
