"""yt-dlp integration for transcript extraction."""

import logging
import tempfile
from pathlib import Path

import yt_dlp

from study.core.config import Settings
from study.core.models import TranscriptResult, TranscriptSegment
from study.transcript.parser import parse_subtitle_file

logger = logging.getLogger("study")


def _build_ydl_opts(settings: Settings, temp_dir: Path) -> dict:
    """Build the yt-dlp options dictionary."""
    opts: dict = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": [settings.transcript_lang],
        "subtitlesformat": settings.subtitle_format,
        "outtmpl": str(temp_dir / "%(id)s.%(ext)s"),
        "quiet": not settings.verbose,
        "no_warnings": not settings.verbose,
        "ignoreerrors": True,
        "download_archive": str(settings.archive_file.resolve()),
    }
    return opts


def _build_ydl_opts_with_date(
    settings: Settings, temp_dir: Path, after_date: str | None = None
) -> dict:
    """Build yt-dlp options with optional date filter."""
    opts = _build_ydl_opts(settings, temp_dir)
    if after_date:
        from yt_dlp.utils import DateRange

        opts["daterange"] = DateRange(start=after_date)
    return opts


def _find_subtitle_file(
    entry: dict, settings: Settings, temp_dir: Path
) -> Path | None:
    """Locate the subtitle file for a video entry."""
    requested_subs = entry.get("requested_subtitles") or {}
    sub_info = requested_subs.get(settings.transcript_lang)
    if not sub_info:
        if requested_subs:
            sub_info = next(iter(requested_subs.values()))

    if sub_info:
        filepath = sub_info.get("filepath")
        if filepath and Path(filepath).exists():
            return Path(filepath)

    video_id = entry.get("id", "")
    if video_id:
        for path in temp_dir.iterdir():
            if path.stem.startswith(video_id) and path.suffix in (
                ".json3",
                ".vtt",
                ".srt",
            ):
                return path

    return None


def _detect_format(filepath: Path, settings: Settings) -> str:
    """Detect subtitle format from file extension, falling back to config."""
    ext = filepath.suffix.lstrip(".")
    if ext in ("json3", "vtt", "srt"):
        return ext
    return settings.subtitle_format


def _process_entry(
    entry: dict, settings: Settings, temp_dir: Path
) -> TranscriptResult | None:
    """Process a single video entry into a TranscriptResult."""
    video_id = entry.get("id", "")
    title = entry.get("title") or "Unknown"
    channel = entry.get("channel") or entry.get("uploader") or "Unknown"
    upload_date = entry.get("upload_date") or "00000000"
    webpage_url = entry.get("webpage_url") or ""

    sub_path = _find_subtitle_file(entry, settings, temp_dir)
    if not sub_path:
        logger.warning("No transcript found for: %s", title)
        return None

    fmt = _detect_format(sub_path, settings)

    try:
        segments = parse_subtitle_file(sub_path, fmt)
    except Exception as e:
        logger.error("Failed to parse subtitles for %s: %s", title, e)
        return None

    return TranscriptResult(
        id=video_id,
        title=title,
        channel=channel,
        upload_date=upload_date,
        webpage_url=webpage_url,
        transcript=segments,
    )


def _flatten_entries(info: dict) -> list[dict]:
    """Recursively flatten playlist/channel entries."""
    if info is None:
        return []
    entries = info.get("entries")
    if entries is None:
        return [info]
    result = []
    for entry in entries:
        if entry is None:
            continue
        result.extend(_flatten_entries(entry))
    return result


def extract_transcripts(
    urls: list[str],
    settings: Settings,
    after_date: str | None = None,
) -> list[TranscriptResult]:
    """Extract transcripts from a list of URLs (videos, channels, or playlists)."""
    results: list[TranscriptResult] = []

    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        ydl_opts = _build_ydl_opts_with_date(settings, temp_dir, after_date)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for url in urls:
                logger.info("Processing: %s", url)
                try:
                    info = ydl.extract_info(url, download=True)
                except Exception as e:
                    logger.error("Failed to process %s: %s", url, e)
                    continue

                if info is None:
                    continue

                entries = _flatten_entries(info)
                for entry in entries:
                    result = _process_entry(entry, settings, temp_dir)
                    if result:
                        results.append(result)

    logger.info("Extracted %d transcript(s)", len(results))
    return results


def extract_channel(
    channel_url: str,
    settings: Settings,
    after_date: str | None = None,
) -> list[TranscriptResult]:
    """Extract transcripts from a YouTube channel."""
    return extract_transcripts([channel_url], settings, after_date=after_date)


def extract_playlist(
    playlist_url: str, settings: Settings
) -> list[TranscriptResult]:
    """Extract transcripts from a playlist."""
    return extract_transcripts([playlist_url], settings)
