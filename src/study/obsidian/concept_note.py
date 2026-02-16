"""Concept note generator with merge logic for Obsidian vault."""

from datetime import datetime, timezone
from pathlib import Path

from study.core.models import Concept
from study.obsidian.frontmatter import parse_frontmatter, serialize_frontmatter
from study.obsidian.vault import Vault


def create_or_update_concept(
    vault: Vault,
    concept: Concept,
    source_video_title: str,
) -> Path:
    """Create concept note or add source to existing one."""
    note_path = vault.concept_note_path(concept.name)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    source_link = f"[[{source_video_title}]]"

    if note_path.exists():
        return _update_existing(note_path, source_link, now)

    return _create_new(note_path, concept, source_link, now)


def _create_new(
    note_path: Path,
    concept: Concept,
    source_link: str,
    now: str,
) -> Path:
    frontmatter = {
        "type": "concept",
        "name": concept.name,
        "created": now,
        "updated": now,
        "sources": [source_link],
        "tags": ["concept"],
    }

    body = (
        f"# {concept.name}\n\n"
        f"## Definicao\n\n{concept.definition}\n\n"
        f"## Explicado em\n\n- {source_link}\n"
    )

    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(serialize_frontmatter(frontmatter) + body, encoding="utf-8")
    return note_path


def _update_existing(note_path: Path, source_link: str, now: str) -> Path:
    content = note_path.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(content)

    sources = metadata.get("sources", [])
    if source_link in sources:
        return note_path

    sources.append(source_link)
    metadata["sources"] = sources
    metadata["updated"] = now

    if f"- {source_link}" not in body:
        body = body.rstrip("\n") + f"\n- {source_link}\n"

    note_path.write_text(serialize_frontmatter(metadata) + body, encoding="utf-8")
    return note_path
