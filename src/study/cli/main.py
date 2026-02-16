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
    typer.echo("Status: not implemented yet")


@app.command()
def config() -> None:
    """Show current configuration."""
    typer.echo("Config: not implemented yet")
