"""Tests for config module."""

import pytest
from pathlib import Path

from study.core.config import load_settings


class TestLoadSettings:
    def test_defaults(self, tmp_path: Path, monkeypatch):
        vault = tmp_path / "vault"
        vault.mkdir()
        monkeypatch.delenv("VAULT_PATH", raising=False)
        monkeypatch.delenv("CLAUDE_BACKEND", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        settings = load_settings(vault_path=str(vault))
        assert settings.vault_path == vault
        assert settings.claude_backend == "api"
        assert settings.claude_model == "claude-sonnet-4-5-20250929"
        assert settings.transcript_lang == "en"
        assert settings.subtitle_format == "json3"
        assert settings.content_lang == "pt-BR"
        assert settings.verbose is False

    def test_overrides(self, tmp_path: Path, monkeypatch):
        vault = tmp_path / "vault"
        vault.mkdir()
        monkeypatch.delenv("VAULT_PATH", raising=False)
        monkeypatch.delenv("CLAUDE_BACKEND", raising=False)

        settings = load_settings(
            vault_path=str(vault),
            claude_backend="cli",
            transcript_lang="pt",
        )
        assert settings.claude_backend == "cli"
        assert settings.transcript_lang == "pt"

    def test_env_vars(self, tmp_path: Path, monkeypatch):
        vault = tmp_path / "vault"
        vault.mkdir()
        monkeypatch.setenv("VAULT_PATH", str(vault))
        monkeypatch.setenv("CLAUDE_BACKEND", "cli")
        monkeypatch.setenv("TRANSCRIPT_LANG", "pt")

        settings = load_settings()
        assert settings.vault_path == vault
        assert settings.claude_backend == "cli"
        assert settings.transcript_lang == "pt"

    def test_invalid_backend_raises(self, tmp_path: Path, monkeypatch):
        vault = tmp_path / "vault"
        vault.mkdir()
        monkeypatch.delenv("CLAUDE_BACKEND", raising=False)

        with pytest.raises(ValueError, match="claude_backend"):
            load_settings(vault_path=str(vault), claude_backend="invalid")

    def test_nonexistent_vault_raises(self, tmp_path: Path, monkeypatch):
        monkeypatch.delenv("VAULT_PATH", raising=False)

        with pytest.raises(ValueError, match="vault_path"):
            load_settings(vault_path=str(tmp_path / "nonexistent"))

    def test_empty_vault_path_no_error(self, monkeypatch):
        monkeypatch.delenv("VAULT_PATH", raising=False)
        settings = load_settings()
        assert str(settings.vault_path) == "."
