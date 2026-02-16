"""Vault management operations for Obsidian."""

from pathlib import Path

from study.core.utils import sanitize_filename
from study.obsidian.frontmatter import parse_frontmatter


class Vault:
    """Manages paths and structure within an Obsidian vault."""

    def __init__(self, vault_path: Path):
        self.root = vault_path
        self.sources_dir = vault_path / "Sources" / "YouTube"
        self.concepts_dir = vault_path / "Concepts"

    def ensure_structure(self) -> None:
        """Create base vault directories if they don't exist."""
        self.sources_dir.mkdir(parents=True, exist_ok=True)
        self.concepts_dir.mkdir(parents=True, exist_ok=True)

    def channel_dir(self, channel_name: str) -> Path:
        """Return path: Sources/YouTube/{channel}/"""
        return self.sources_dir / sanitize_filename(channel_name)

    def video_note_path(self, channel_name: str, video_title: str) -> Path:
        """Return path: Sources/YouTube/{channel}/Videos/{title}.md"""
        return (
            self.channel_dir(channel_name)
            / "Videos"
            / f"{sanitize_filename(video_title)}.md"
        )

    def concept_note_path(self, concept_name: str) -> Path:
        """Return path: Concepts/{concept}.md"""
        return self.concepts_dir / f"{sanitize_filename(concept_name)}.md"

    def channel_note_path(self, channel_name: str) -> Path:
        """Return path: Sources/YouTube/{channel}/{channel}.md"""
        safe = sanitize_filename(channel_name)
        return self.sources_dir / safe / f"{safe}.md"

    def video_note_exists(self, video_id: str) -> bool:
        """Check if a video note already exists (by scanning frontmatter)."""
        for md_file in self.sources_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                metadata, _ = parse_frontmatter(content)
                if metadata.get("video_id") == video_id:
                    return True
            except (OSError, UnicodeDecodeError):
                continue
        return False

    def concept_note_exists(self, concept_name: str) -> bool:
        """Check if concept note exists."""
        return self.concept_note_path(concept_name).exists()
