"""yt-dlp integration for transcript extraction."""

import logging
import tempfile
from pathlib import Path

import yt_dlp

from .config import ExtractorConfig, TranscriptResult, TranscriptSegment
from .parser import parse_subtitle_file, write_result
from .utils import build_output_path

logger = logging.getLogger("yt_transcript_extractor")


def _is_archived(archive_file: Path, entry: dict) -> bool:
    """Check if a video is already recorded in the archive file."""
    video_id = entry.get("id", "")
    if not video_id:
        return False
    archive_path = archive_file.resolve()
    if not archive_path.exists():
        return False
    content = archive_path.read_text()
    return f" {video_id}" in content


def _record_in_archive(archive_file: Path, entry: dict) -> None:
    """Append video to archive file if not already present."""
    video_id = entry.get("id", "")
    extractor = entry.get("extractor", "youtube")
    if not video_id:
        return
    archive_path = archive_file.resolve()
    archive_line = f"{extractor} {video_id}\n"
    if archive_path.exists():
        content = archive_path.read_text()
        if f" {video_id}" in content:
            return
    with open(archive_path, "a") as f:
        f.write(archive_line)


def _build_ydl_opts(config: ExtractorConfig, temp_dir: Path) -> dict:
    """Build the yt-dlp options dictionary."""
    opts: dict = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": [config.lang],
        "subtitlesformat": config.subtitle_format,
        "outtmpl": str(temp_dir / "%(id)s.%(ext)s"),
        "quiet": not config.verbose,
        "no_warnings": not config.verbose,
        "ignoreerrors": True,
        "download_archive": str(config.archive_file.resolve()),
    }
    if config.after_date:
        from yt_dlp.utils import DateRange

        opts["daterange"] = DateRange(start=config.after_date)
    return opts


def _find_subtitle_file(entry: dict, config: ExtractorConfig, temp_dir: Path) -> Path | None:
    """Locate the subtitle file for a video entry."""
    # Try from requested_subtitles metadata
    requested_subs = entry.get("requested_subtitles") or {}
    sub_info = requested_subs.get(config.lang)
    if not sub_info:
        # Try any available language
        if requested_subs:
            sub_info = next(iter(requested_subs.values()))

    if sub_info:
        filepath = sub_info.get("filepath")
        if filepath and Path(filepath).exists():
            return Path(filepath)

    # Fallback: scan temp directory for matching files
    video_id = entry.get("id", "")
    if video_id:
        for path in temp_dir.iterdir():
            if path.stem.startswith(video_id) and path.suffix in (".json3", ".vtt", ".srt"):
                return path

    return None


def _detect_format(filepath: Path, config: ExtractorConfig) -> str:
    """Detect subtitle format from file extension, falling back to config."""
    ext = filepath.suffix.lstrip(".")
    if ext in ("json3", "vtt", "srt"):
        return ext
    return config.subtitle_format


def _process_entry(
    entry: dict, config: ExtractorConfig, temp_dir: Path
) -> TranscriptResult | None:
    """Process a single video entry into a TranscriptResult."""
    video_id = entry.get("id", "")
    title = entry.get("title") or "Unknown"
    channel = entry.get("channel") or entry.get("uploader") or "Unknown"
    upload_date = entry.get("upload_date") or "00000000"
    webpage_url = entry.get("webpage_url") or ""

    if _is_archived(config.archive_file, entry):
        logger.info("Skipping (already archived): %s", title)
        return None

    sub_path = _find_subtitle_file(entry, config, temp_dir)
    if not sub_path:
        logger.warning("No transcript found for: %s", title)
        return None

    fmt = _detect_format(sub_path, config)

    try:
        segments = parse_subtitle_file(sub_path, fmt)
    except Exception as e:
        logger.error("Failed to parse subtitles for %s: %s", title, e)
        return None

    result = TranscriptResult(
        id=video_id,
        title=title,
        channel=channel,
        upload_date=upload_date,
        webpage_url=webpage_url,
        transcript=segments,
    )

    output_path = build_output_path(config.output_dir, channel, upload_date, title)
    write_result(result, output_path)
    _record_in_archive(config.archive_file, entry)
    logger.info("Saved transcript: %s", output_path)

    return result


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
    urls: list[str], config: ExtractorConfig
) -> list[TranscriptResult]:
    """Extract transcripts from a list of URLs (videos, channels, or playlists).

    This is the main public API for library usage.
    """
    results: list[TranscriptResult] = []

    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        ydl_opts = _build_ydl_opts(config, temp_dir)

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
                    result = _process_entry(entry, config, temp_dir)
                    if result:
                        results.append(result)

    logger.info("Extracted %d transcript(s)", len(results))
    return results


def extract_channel(
    channel_url: str, config: ExtractorConfig
) -> list[TranscriptResult]:
    """Extract transcripts from a YouTube channel."""
    return extract_transcripts([channel_url], config)


def extract_playlist(
    playlist_urls: list[str], config: ExtractorConfig
) -> list[TranscriptResult]:
    """Extract transcripts from one or more playlists."""
    return extract_transcripts(playlist_urls, config)
