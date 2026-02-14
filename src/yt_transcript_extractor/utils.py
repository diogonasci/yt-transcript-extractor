"""Utility functions: logging, filename sanitization, path helpers."""

import logging
import re
from pathlib import Path

logger = logging.getLogger("yt_transcript_extractor")


def setup_logging(verbose: bool = False) -> None:
    """Configure logging with the appropriate level and format."""
    level = logging.DEBUG if verbose else logging.INFO
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    root = logging.getLogger("yt_transcript_extractor")
    root.setLevel(level)
    root.addHandler(handler)


def sanitize_filename(name: str) -> str:
    """Remove or replace characters that are invalid in filenames."""
    # Replace problematic characters with underscore
    sanitized = re.sub(r'[\\/:*?"<>|]', "_", name)
    # Collapse multiple underscores/spaces
    sanitized = re.sub(r"_+", "_", sanitized)
    sanitized = sanitized.strip(" _.")
    # Truncate to 200 characters
    if len(sanitized) > 200:
        sanitized = sanitized[:200].rstrip(" _.")
    return sanitized or "untitled"


def build_output_path(
    output_dir: Path,
    channel: str,
    upload_date: str,
    title: str,
) -> Path:
    """Build the output file path: output_dir/channel/YYYYMMDD - Title.json"""
    channel_dir = output_dir / sanitize_filename(channel)
    filename = f"{upload_date} - {sanitize_filename(title)}.json"
    path = channel_dir / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
