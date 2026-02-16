"""YAML frontmatter serializer/deserializer for Obsidian notes."""

import yaml


def serialize_frontmatter(metadata: dict) -> str:
    """Convert dict to YAML frontmatter string (with --- delimiters)."""
    yaml_str = yaml.dump(
        metadata,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    )
    return f"---\n{yaml_str}---\n"


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse markdown file content into (frontmatter_dict, body_text)."""
    if not content.startswith("---"):
        return {}, content

    end_idx = content.find("---", 3)
    if end_idx == -1:
        return {}, content

    yaml_str = content[3:end_idx].strip()
    body = content[end_idx + 3:].lstrip("\n")

    metadata = yaml.safe_load(yaml_str) or {}
    return metadata, body


def update_frontmatter(content: str, updates: dict) -> str:
    """Update specific frontmatter fields without touching the body."""
    metadata, body = parse_frontmatter(content)
    metadata.update(updates)
    return serialize_frontmatter(metadata) + body
