"""Commands for full pipeline: transcript + AI + notes."""

import typer

ingest_app = typer.Typer(help="Full pipeline: transcript + AI + notes")


@ingest_app.command()
def video(url: str) -> None:
    """Ingest a single video: extract transcript, process with AI, generate notes."""
    typer.echo(f"ingest video: not implemented yet ({url})")


@ingest_app.command()
def playlist(url: str) -> None:
    """Ingest all videos from a playlist."""
    typer.echo(f"ingest playlist: not implemented yet ({url})")


@ingest_app.command()
def channel(
    url: str,
    after: str | None = typer.Option(None, help="Only videos after YYYYMMDD"),
) -> None:
    """Ingest all videos from a channel."""
    typer.echo(f"ingest channel: not implemented yet ({url})")
