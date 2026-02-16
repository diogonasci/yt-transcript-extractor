"""Commands for AI processing of existing transcripts."""

from typing import Optional

import typer

process_app = typer.Typer(help="Process transcripts with AI")


@process_app.command()
def run(
    video_id: Optional[str] = typer.Argument(None, help="Video ID to process"),
    all_pending: bool = typer.Option(False, "--all", help="Process all pending"),
    reprocess: bool = typer.Option(False, help="Force reprocessing"),
) -> None:
    """Process transcript(s) with AI."""
    if all_pending:
        typer.echo("process --all: not implemented yet")
    elif video_id:
        typer.echo(f"process {video_id}: not implemented yet")
    else:
        typer.echo("Provide a video_id or use --all")
        raise typer.Exit(1)
