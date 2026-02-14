"""Configuration, constants, and data types."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

DEFAULT_OUTPUT_DIR = Path("transcripts")
DEFAULT_LANG = "en"
DEFAULT_ARCHIVE = Path("archive.txt")
DEFAULT_FORMAT = "json3"

SubtitleFormat = Literal["json3", "vtt", "srt"]


@dataclass
class ExtractorConfig:
    """Configuration for transcript extraction."""

    output_dir: Path = DEFAULT_OUTPUT_DIR
    lang: str = DEFAULT_LANG
    archive_file: Path = DEFAULT_ARCHIVE
    subtitle_format: SubtitleFormat = DEFAULT_FORMAT
    verbose: bool = False
    after_date: str | None = None  # YYYYMMDD


@dataclass
class TranscriptSegment:
    """A single segment of a transcript."""

    text: str
    start: float
    duration: float


@dataclass
class TranscriptResult:
    """Complete transcript with video metadata."""

    id: str
    title: str
    channel: str
    upload_date: str
    webpage_url: str
    transcript: list[TranscriptSegment] = field(default_factory=list)
