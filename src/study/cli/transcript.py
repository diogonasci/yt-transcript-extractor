"""Commands for transcript extraction only (no AI)."""

import typer

from study.core.config import load_settings
from study.core.state import ProcessingStateManager
from study.core.utils import setup_logging, logger
from study.transcript.extractor import extract_transcripts, extract_channel, extract_playlist
from study.transcript.storage import TranscriptStorage

transcript_app = typer.Typer(help="Extract and save transcripts (no AI processing)")


def _save_results(results, storage, state, force: bool) -> tuple[int, int]:
    """Save extraction results, returning (saved, skipped) counts."""
    saved = 0
    skipped = 0
    for result in results:
        if state.is_transcript_extracted(result.id) and not force:
            logger.info("Skipping (already extracted): %s", result.title)
            skipped += 1
            continue
        path = storage.save(result)
        state.update(result.id, transcript_extracted=True)
        logger.info("Saved: %s -> %s", result.title, path)
        saved += 1
    return saved, skipped


@transcript_app.command()
def video(
    url: str,
    lang: str = typer.Option("en", help="Subtitle language"),
    format: str = typer.Option("json3", help="Subtitle format (json3, vtt, srt)"),
    force: bool = typer.Option(False, help="Re-extract even if already exists"),
    verbose: bool = typer.Option(False, help="Enable verbose output"),
) -> None:
    """Extract transcript from a single video."""
    setup_logging(verbose)
    settings = load_settings(
        transcript_lang=lang, subtitle_format=format, verbose=verbose
    )
    storage = TranscriptStorage(settings.data_dir)
    state = ProcessingStateManager(settings.data_dir / "processing_state.json")

    results = extract_transcripts([url], settings, state=state, force=force)
    saved, skipped = _save_results(results, storage, state, force)

    typer.echo(f"Done: {saved} saved, {skipped} skipped")


@transcript_app.command()
def playlist(
    url: str,
    lang: str = typer.Option("en", help="Subtitle language"),
    format: str = typer.Option("json3", help="Subtitle format"),
    force: bool = typer.Option(False, help="Re-extract even if already exists"),
    verbose: bool = typer.Option(False, help="Enable verbose output"),
) -> None:
    """Extract transcripts from a playlist."""
    setup_logging(verbose)
    settings = load_settings(
        transcript_lang=lang, subtitle_format=format, verbose=verbose
    )
    storage = TranscriptStorage(settings.data_dir)
    state = ProcessingStateManager(settings.data_dir / "processing_state.json")

    results = extract_playlist(url, settings, state=state, force=force)
    saved, skipped = _save_results(results, storage, state, force)

    typer.echo(f"Done: {saved} saved, {skipped} skipped")


@transcript_app.command()
def channel(
    url: str,
    lang: str = typer.Option("en", help="Subtitle language"),
    format: str = typer.Option("json3", help="Subtitle format"),
    after: str | None = typer.Option(None, help="Only videos after YYYYMMDD"),
    force: bool = typer.Option(False, help="Re-extract even if already exists"),
    verbose: bool = typer.Option(False, help="Enable verbose output"),
) -> None:
    """Extract transcripts from a channel."""
    setup_logging(verbose)
    settings = load_settings(
        transcript_lang=lang, subtitle_format=format, verbose=verbose
    )
    storage = TranscriptStorage(settings.data_dir)
    state = ProcessingStateManager(settings.data_dir / "processing_state.json")

    results = extract_channel(url, settings, after_date=after, state=state, force=force)
    saved, skipped = _save_results(results, storage, state, force)

    typer.echo(f"Done: {saved} saved, {skipped} skipped")
