"""Main CLI application with typer."""

import typer

from study.cli.ingest import ingest_app
from study.cli.transcript import transcript_app
from study.cli.process import process_app

app = typer.Typer(name="study", help="YouTube -> Obsidian Knowledge Compiler")

app.add_typer(ingest_app, name="ingest")
app.add_typer(transcript_app, name="transcript")
app.add_typer(process_app, name="process")


@app.command()
def status() -> None:
    """Show processing status."""
    from study.core.config import load_settings
    from study.core.state import ProcessingStateManager
    from study.transcript.storage import TranscriptStorage

    try:
        settings = load_settings()
    except ValueError:
        settings = None

    if settings is None:
        typer.echo("Error: could not load settings. Check your .env file.")
        raise typer.Exit(1)

    storage = TranscriptStorage(settings.data_dir)
    state = ProcessingStateManager(settings.data_dir / "processing_state.json")

    all_ids = storage.list_all()
    transcript_count = len(all_ids)

    ai_done = sum(1 for vid in all_ids if state.is_ai_processed(vid))
    ai_pending = transcript_count - ai_done

    notes_done = sum(1 for vid in all_ids if state.is_notes_generated(vid))
    notes_pending = transcript_count - notes_done

    typer.echo("Study -- Processing Status\n")
    typer.echo(f"Transcripts:  {transcript_count} extracted")
    typer.echo(f"AI processed: {ai_done} completed, {ai_pending} pending")
    typer.echo(f"Notes:        {notes_done} generated, {notes_pending} pending")

    pending = state.pending_ai_processing()
    if pending:
        typer.echo("\nPending AI processing:")
        for vid in pending:
            transcript = storage.load(vid)
            title = transcript.title if transcript else vid
            typer.echo(f"  - {vid} ({title})")


@app.command()
def config() -> None:
    """Show current configuration."""
    from study.core.config import load_settings

    try:
        settings = load_settings()
    except ValueError as e:
        typer.echo(f"Error loading config: {e}")
        raise typer.Exit(1)

    def _mask_key(key: str) -> str:
        if not key or len(key) <= 4:
            return "****" if key else "(not set)"
        return f"****{key[-4:]}"

    typer.echo("Study -- Configuration\n")
    typer.echo(f"Vault path:      {settings.vault_path}")
    typer.echo(f"Claude backend:  {settings.claude_backend}")
    typer.echo(f"API key:         {_mask_key(settings.anthropic_api_key)}")
    typer.echo(f"Claude model:    {settings.claude_model}")
    typer.echo(f"Transcript lang: {settings.transcript_lang}")
    typer.echo(f"Content lang:    {settings.content_lang}")
    typer.echo(f"Subtitle format: {settings.subtitle_format}")
    typer.echo(f"Data dir:        {settings.data_dir}")
