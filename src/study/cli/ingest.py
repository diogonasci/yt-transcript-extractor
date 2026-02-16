"""Commands for full pipeline: transcript + AI + notes."""

import json
import logging
from pathlib import Path
from typing import Optional

import typer

from study.ai import create_backend
from study.core.config import load_settings
from study.core.models import AIResponse, TranscriptResult
from study.core.state import ProcessingStateManager
from study.core.utils import setup_logging
from study.obsidian.channel_note import create_or_update_channel
from study.obsidian.concept_note import create_or_update_concept
from study.obsidian.vault import Vault
from study.obsidian.video_note import create_video_note
from study.transcript.extractor import extract_transcripts, extract_channel, extract_playlist
from study.transcript.storage import TranscriptStorage

logger = logging.getLogger("study")

ingest_app = typer.Typer(help="Full pipeline: transcript + AI + notes")


def _save_ai_response(data_dir: Path, video_id: str, response: AIResponse) -> Path:
    """Save AIResponse as JSON in data/ai_responses/{video_id}.json."""
    out_dir = data_dir / "ai_responses"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{video_id}.json"
    data = {
        "tldr": response.tldr,
        "summary": response.summary,
        "concepts": [{"name": c.name, "definition": c.definition} for c in response.concepts],
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def _load_ai_response(data_dir: Path, video_id: str) -> AIResponse | None:
    """Load AIResponse from JSON if it exists."""
    from study.core.models import Concept
    path = data_dir / "ai_responses" / f"{video_id}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return AIResponse(
        tldr=data["tldr"],
        summary=data["summary"],
        concepts=[Concept(name=c["name"], definition=c["definition"]) for c in data.get("concepts", [])],
    )


def _run_pipeline(
    results: list[TranscriptResult],
    settings,
    storage: TranscriptStorage,
    state: ProcessingStateManager,
    force: bool,
    reprocess: bool,
) -> dict:
    """Run the full pipeline on a list of TranscriptResults. Returns summary counts."""
    vault = Vault(settings.vault_path)
    vault.ensure_structure()

    counts = {"transcripts_saved": 0, "transcripts_skipped": 0, "ai_processed": 0, "ai_failed": 0, "notes_generated": 0}

    for result in results:
        # Step 1: Save transcript
        if state.is_transcript_extracted(result.id) and not force:
            logger.info("Transcript already exists: %s", result.title)
            counts["transcripts_skipped"] += 1
        else:
            storage.save(result)
            state.update(result.id, transcript_extracted=True)
            logger.info("Transcript saved: %s", result.title)
            counts["transcripts_saved"] += 1

        # Step 2: AI processing
        ai_response = None
        if state.is_ai_processed(result.id) and not reprocess:
            logger.info("AI already processed: %s", result.title)
            ai_response = _load_ai_response(settings.data_dir, result.id)
        else:
            typer.echo(f"  Processing with AI: {result.title}")
            try:
                backend = create_backend(settings)
                ai_response = backend.process_transcript(result.full_text, result.title)
                _save_ai_response(settings.data_dir, result.id, ai_response)
                state.update(result.id, ai_processed=True)
                counts["ai_processed"] += 1
            except (RuntimeError, ValueError) as e:
                logger.error("AI processing failed for %s: %s", result.id, e)
                typer.echo(f"  AI failed for {result.id}: {e}")
                counts["ai_failed"] += 1
                continue

        if ai_response is None:
            logger.warning("No AI response for %s, skipping notes", result.id)
            continue

        # Step 3: Generate Obsidian notes
        if state.is_notes_generated(result.id) and not reprocess:
            logger.info("Notes already generated: %s", result.title)
            continue

        create_video_note(vault, result, ai_response)

        for concept in ai_response.concepts:
            create_or_update_concept(vault, concept, result.title)

        channel_url = result.webpage_url.rsplit("/watch", 1)[0] if "/watch" in result.webpage_url else result.webpage_url
        create_or_update_channel(vault, result.channel, channel_url, result.title)

        state.update(result.id, notes_generated=True)
        counts["notes_generated"] += 1
        typer.echo(f"  Notes generated: {result.title}")

    return counts


def _print_summary(counts: dict) -> None:
    saved = counts["transcripts_saved"]
    skipped = counts["transcripts_skipped"]
    ai_ok = counts["ai_processed"]
    ai_fail = counts["ai_failed"]
    notes = counts["notes_generated"]
    typer.echo(f"\nSummary: {saved} transcripts saved, {skipped} skipped")
    typer.echo(f"  AI: {ai_ok} processed, {ai_fail} failed")
    typer.echo(f"  Notes: {notes} generated")


@ingest_app.command()
def video(
    url: str,
    backend: Optional[str] = typer.Option(None, help="AI backend: api or cli"),
    model: Optional[str] = typer.Option(None, help="Claude model override"),
    lang: str = typer.Option("en", help="Subtitle language"),
    format: str = typer.Option("json3", help="Subtitle format"),
    force: bool = typer.Option(False, help="Re-extract transcript"),
    reprocess: bool = typer.Option(False, help="Re-process with AI"),
    verbose: bool = typer.Option(False, help="Verbose output"),
) -> None:
    """Ingest a single video: extract transcript, process with AI, generate notes."""
    setup_logging(verbose)
    overrides: dict = {"transcript_lang": lang, "subtitle_format": format, "verbose": verbose}
    if backend:
        overrides["claude_backend"] = backend
    if model:
        overrides["claude_model"] = model

    settings = load_settings(**overrides)
    storage = TranscriptStorage(settings.data_dir)
    state = ProcessingStateManager(settings.data_dir / "processing_state.json")

    typer.echo(f"Ingesting video: {url}")
    results = extract_transcripts([url], settings)
    counts = _run_pipeline(results, settings, storage, state, force, reprocess)
    _print_summary(counts)


@ingest_app.command()
def playlist(
    url: str,
    backend: Optional[str] = typer.Option(None, help="AI backend: api or cli"),
    model: Optional[str] = typer.Option(None, help="Claude model override"),
    lang: str = typer.Option("en", help="Subtitle language"),
    format: str = typer.Option("json3", help="Subtitle format"),
    after: Optional[str] = typer.Option(None, help="Only videos after YYYYMMDD"),
    force: bool = typer.Option(False, help="Re-extract transcript"),
    reprocess: bool = typer.Option(False, help="Re-process with AI"),
    verbose: bool = typer.Option(False, help="Verbose output"),
) -> None:
    """Ingest all videos from a playlist."""
    setup_logging(verbose)
    overrides: dict = {"transcript_lang": lang, "subtitle_format": format, "verbose": verbose}
    if backend:
        overrides["claude_backend"] = backend
    if model:
        overrides["claude_model"] = model

    settings = load_settings(**overrides)
    storage = TranscriptStorage(settings.data_dir)
    state = ProcessingStateManager(settings.data_dir / "processing_state.json")

    typer.echo(f"Ingesting playlist: {url}")
    results = extract_playlist(url, settings)
    counts = _run_pipeline(results, settings, storage, state, force, reprocess)
    _print_summary(counts)


@ingest_app.command()
def channel(
    url: str,
    backend: Optional[str] = typer.Option(None, help="AI backend: api or cli"),
    model: Optional[str] = typer.Option(None, help="Claude model override"),
    lang: str = typer.Option("en", help="Subtitle language"),
    format: str = typer.Option("json3", help="Subtitle format"),
    after: Optional[str] = typer.Option(None, help="Only videos after YYYYMMDD"),
    force: bool = typer.Option(False, help="Re-extract transcript"),
    reprocess: bool = typer.Option(False, help="Re-process with AI"),
    verbose: bool = typer.Option(False, help="Verbose output"),
) -> None:
    """Ingest all videos from a channel."""
    setup_logging(verbose)
    overrides: dict = {"transcript_lang": lang, "subtitle_format": format, "verbose": verbose}
    if backend:
        overrides["claude_backend"] = backend
    if model:
        overrides["claude_model"] = model

    settings = load_settings(**overrides)
    storage = TranscriptStorage(settings.data_dir)
    state = ProcessingStateManager(settings.data_dir / "processing_state.json")

    typer.echo(f"Ingesting channel: {url}")
    results = extract_channel(url, settings, after_date=after)
    counts = _run_pipeline(results, settings, storage, state, force, reprocess)
    _print_summary(counts)
