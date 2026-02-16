"""Channel index note generator for Obsidian vault."""

from datetime import datetime, timezone
from pathlib import Path

from study.obsidian.frontmatter import parse_frontmatter, serialize_frontmatter
from study.obsidian.vault import Vault


def create_or_update_channel(
    vault: Vault,
    channel_name: str,
    channel_url: str,
    video_title: str,
) -> Path:
    """Create channel index or add video to existing one."""
    note_path = vault.channel_note_path(channel_name)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    video_link = f"[[{video_title}]]"

    if note_path.exists():
        return _update_existing(note_path, video_link, now)

    return _create_new(note_path, channel_name, channel_url, video_link, now)


def _create_new(
    note_path: Path,
    channel_name: str,
    channel_url: str,
    video_link: str,
    now: str,
) -> Path:
    frontmatter = {
        "type": "youtube_channel",
        "name": channel_name,
        "url": channel_url,
        "created": now,
        "updated": now,
        "tags": ["youtube", "channel"],
    }

    body = (
        f"# {channel_name}\n\n"
        f"## Videos Processados\n\n- {video_link}\n"
    )

    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(serialize_frontmatter(frontmatter) + body, encoding="utf-8")
    return note_path


def _update_existing(note_path: Path, video_link: str, now: str) -> Path:
    content = note_path.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(content)

    if f"- {video_link}" in body:
        return note_path

    metadata["updated"] = now
    body = body.rstrip("\n") + f"\n- {video_link}\n"

    note_path.write_text(serialize_frontmatter(metadata) + body, encoding="utf-8")
    return note_path
