"""Central configuration loaded from .env with CLI overrides."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Settings:
    """Application settings."""

    vault_path: Path
    claude_backend: str
    anthropic_api_key: str
    claude_model: str
    transcript_lang: str
    subtitle_format: str
    content_lang: str
    data_dir: Path
    archive_file: Path
    verbose: bool


def load_settings(**overrides) -> Settings:
    """Load settings from .env file, with CLI overrides."""
    load_dotenv()

    def _get(key: str, default: str = "") -> str:
        override = overrides.get(key.lower())
        if override is not None:
            return str(override)
        return os.environ.get(key.upper(), default)

    vault_path = Path(_get("vault_path", ""))
    claude_backend = _get("claude_backend", "api")
    anthropic_api_key = _get("anthropic_api_key", "")
    claude_model = _get("claude_model", "claude-sonnet-4-5-20250929")
    transcript_lang = _get("transcript_lang", "en")
    subtitle_format = _get("subtitle_format", "json3")
    content_lang = _get("content_lang", "pt-BR")
    data_dir = Path(_get("data_dir", "data"))
    archive_file_str = _get("archive_file", "")
    archive_file = Path(archive_file_str) if archive_file_str else data_dir / "archive.txt"
    verbose = _get("verbose", "false").lower() in ("true", "1", "yes")

    if claude_backend not in ("api", "cli"):
        raise ValueError(f"claude_backend must be 'api' or 'cli', got '{claude_backend}'")

    if str(vault_path) and not vault_path.exists():
        raise ValueError(f"vault_path does not exist: {vault_path}")

    return Settings(
        vault_path=vault_path,
        claude_backend=claude_backend,
        anthropic_api_key=anthropic_api_key,
        claude_model=claude_model,
        transcript_lang=transcript_lang,
        subtitle_format=subtitle_format,
        content_lang=content_lang,
        data_dir=data_dir,
        archive_file=archive_file,
        verbose=verbose,
    )
