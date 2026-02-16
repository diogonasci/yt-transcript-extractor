"""Video note generator for Obsidian vault."""

from datetime import datetime, timezone
from pathlib import Path

from study.core.models import AIResponse, TranscriptResult
from study.obsidian.frontmatter import serialize_frontmatter
from study.obsidian.vault import Vault


def create_video_note(
    vault: Vault,
    transcript: TranscriptResult,
    ai_response: AIResponse,
) -> Path:
    """Create or update a video note in the vault. Returns path to note."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    concept_links = [f"[[{c.name}]]" for c in ai_response.concepts]

    frontmatter = {
        "type": "youtube_video",
        "video_id": transcript.id,
        "title": transcript.title,
        "channel": transcript.channel,
        "url": transcript.webpage_url,
        "upload_date": transcript.upload_date,
        "created": now,
        "updated": now,
        "concepts": concept_links,
        "tags": ["youtube"],
        "status": "complete",
    }

    concept_list = "\n".join(f"- [[{c.name}]]" for c in ai_response.concepts)

    body = (
        f"# {transcript.title}\n\n"
        f"## TLDR\n\n{ai_response.tldr}\n\n---\n\n"
        f"## Resumo\n\n{ai_response.summary}\n\n---\n\n"
        f"## Conceitos\n\n{concept_list}\n"
    )

    note_path = vault.video_note_path(transcript.channel, transcript.title)
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(serialize_frontmatter(frontmatter) + body, encoding="utf-8")

    return note_path
