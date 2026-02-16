"""Commands for transcript extraction only (no AI)."""

import typer

transcript_app = typer.Typer(help="Extract and save transcripts (no AI processing)")


@transcript_app.command()
def video(
    url: str,
    lang: str = typer.Option("en", help="Subtitle language"),
    format: str = typer.Option("json3", help="Subtitle format (json3, vtt, srt)"),
    force: bool = typer.Option(False, help="Re-extract even if already exists"),
    verbose: bool = typer.Option(False, help="Enable verbose output"),
) -> None:
    """Extract transcript from a single video."""
    typer.echo(f"transcript video: not implemented yet ({url})")


@transcript_app.command()
def playlist(
    url: str,
    lang: str = typer.Option("en", help="Subtitle language"),
    format: str = typer.Option("json3", help="Subtitle format"),
    force: bool = typer.Option(False, help="Re-extract even if already exists"),
    verbose: bool = typer.Option(False, help="Enable verbose output"),
) -> None:
    """Extract transcripts from a playlist."""
    typer.echo(f"transcript playlist: not implemented yet ({url})")


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
    typer.echo(f"transcript channel: not implemented yet ({url})")
