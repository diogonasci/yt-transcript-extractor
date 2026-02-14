"""Command-line interface for yt-transcript-extractor."""

import argparse
import sys
from pathlib import Path

from .config import (
    DEFAULT_ARCHIVE,
    DEFAULT_FORMAT,
    DEFAULT_LANG,
    DEFAULT_OUTPUT_DIR,
    ExtractorConfig,
)
from .downloader import extract_channel, extract_playlist, extract_transcripts
from .utils import setup_logging


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add common options shared by all subcommands."""
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--lang",
        default=DEFAULT_LANG,
        help=f"Subtitle language (default: {DEFAULT_LANG})",
    )
    parser.add_argument(
        "--archive",
        type=Path,
        default=DEFAULT_ARCHIVE,
        help=f"Archive file for deduplication (default: {DEFAULT_ARCHIVE})",
    )
    parser.add_argument(
        "--format",
        choices=["json3", "vtt", "srt"],
        default=DEFAULT_FORMAT,
        dest="subtitle_format",
        help=f"Subtitle source format (default: {DEFAULT_FORMAT})",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="yt-transcript-extractor",
        description="Extract transcripts from YouTube videos without downloading them",
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # channel mode
    channel_parser = subparsers.add_parser(
        "channel", help="Extract transcripts from a YouTube channel"
    )
    channel_parser.add_argument("url", help="Channel URL")
    channel_parser.add_argument(
        "--after",
        help="Only include videos after this date (YYYYMMDD)",
    )
    _add_common_args(channel_parser)

    # playlist mode
    playlist_parser = subparsers.add_parser(
        "playlist", help="Extract transcripts from one or more playlists"
    )
    playlist_parser.add_argument("urls", nargs="+", help="Playlist URL(s)")
    _add_common_args(playlist_parser)

    # list mode
    list_parser = subparsers.add_parser(
        "list", help="Extract transcripts from a file of video URLs"
    )
    list_parser.add_argument("file", type=Path, help="File with one URL per line")
    _add_common_args(list_parser)

    return parser


def main(argv: list[str] | None = None) -> None:
    """Main entry point for the CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    setup_logging(args.verbose)

    config = ExtractorConfig(
        output_dir=args.output,
        lang=args.lang,
        archive_file=args.archive,
        subtitle_format=args.subtitle_format,
        verbose=args.verbose,
        after_date=getattr(args, "after", None),
    )

    match args.mode:
        case "channel":
            extract_channel(args.url, config)
        case "playlist":
            extract_playlist(args.urls, config)
        case "list":
            file_path: Path = args.file
            if not file_path.exists():
                print(f"Error: file not found: {file_path}", file=sys.stderr)
                sys.exit(1)
            urls = [
                line.strip()
                for line in file_path.read_text().strip().splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
            if not urls:
                print("Error: no URLs found in file", file=sys.stderr)
                sys.exit(1)
            extract_transcripts(urls, config)
