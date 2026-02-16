"""Commands for AI processing of existing transcripts."""

import json
import logging
from pathlib import Path
from typing import Optional

import typer

from study.ai import create_backend
from study.core.config import load_settings
from study.core.models import AIResponse
from study.core.state import ProcessingStateManager
from study.transcript.storage import TranscriptStorage

logger = logging.getLogger("study")

process_app = typer.Typer(help="Process transcripts with AI")


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


def _process_single(
    video_id: str,
    settings,
    storage: TranscriptStorage,
    state: ProcessingStateManager,
    reprocess: bool,
) -> bool:
    """Process a single video_id. Returns True if processed."""
    if state.is_ai_processed(video_id) and not reprocess:
        typer.echo(f"  Skipping {video_id} (already processed)")
        return False

    transcript = storage.load(video_id)
    if transcript is None:
        typer.echo(f"  Error: no transcript found for {video_id}")
        return False

    typer.echo(f"  Processing: {transcript.title}")
    backend = create_backend(settings)
    try:
        response = backend.process_transcript(transcript.full_text, transcript.title)
    except RuntimeError as e:
        typer.echo(f"  Error processing {video_id}: {e}")
        return False

    _save_ai_response(settings.data_dir, video_id, response)
    state.update(video_id, ai_processed=True)
    typer.echo(f"  Done: {video_id}")
    return True


@process_app.command()
def run(
    video_id: Optional[str] = typer.Argument(None, help="Video ID to process"),
    all_pending: bool = typer.Option(False, "--all", help="Process all pending"),
    reprocess: bool = typer.Option(False, "--reprocess", help="Force reprocessing"),
    backend: Optional[str] = typer.Option(None, help="AI backend: api or cli"),
    model: Optional[str] = typer.Option(None, help="Claude model override"),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
) -> None:
    """Process transcript(s) with AI."""
    overrides = {}
    if backend:
        overrides["claude_backend"] = backend
    if model:
        overrides["claude_model"] = model
    if verbose:
        overrides["verbose"] = True

    settings = load_settings(**overrides)
    storage = TranscriptStorage(settings.data_dir)
    state_file = settings.data_dir / "processing_state.json"
    state = ProcessingStateManager(state_file)

    if all_pending:
        pending = state.pending_ai_processing()
        if not pending:
            typer.echo("No pending transcripts to process.")
            return
        typer.echo(f"Processing {len(pending)} pending transcript(s)...")
        processed = sum(
            _process_single(vid, settings, storage, state, reprocess)
            for vid in pending
        )
        typer.echo(f"\nDone: {processed} processed, {len(pending) - processed} skipped/failed")
    elif video_id:
        typer.echo(f"Processing video {video_id}...")
        _process_single(video_id, settings, storage, state, reprocess)
    else:
        typer.echo("Provide a video_id or use --all")
        raise typer.Exit(1)
