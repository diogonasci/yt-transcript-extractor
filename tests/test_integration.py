"""Integration tests for the full pipeline with mocks."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from study.cli.ingest import _run_pipeline, _save_ai_response, _load_ai_response
from study.core.config import Settings
from study.core.models import AIResponse, Concept, TranscriptResult, TranscriptSegment
from study.core.state import ProcessingStateManager
from study.obsidian.frontmatter import parse_frontmatter
from study.obsidian.vault import Vault
from study.transcript.storage import TranscriptStorage


def _make_settings(tmp_path: Path) -> Settings:
    vault_path = tmp_path / "vault"
    vault_path.mkdir()
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return Settings(
        vault_path=vault_path,
        claude_backend="api",
        anthropic_api_key="sk-test-key",
        claude_model="claude-sonnet-4-5-20250929",
        transcript_lang="en",
        subtitle_format="json3",
        content_lang="pt-BR",
        data_dir=data_dir,
        archive_file=data_dir / "archive.txt",
        verbose=False,
    )


def _make_transcript(video_id: str = "abc123", title: str = "Test Video") -> TranscriptResult:
    return TranscriptResult(
        id=video_id,
        title=title,
        channel="Test Channel",
        upload_date="20240115",
        webpage_url="https://youtube.com/watch?v=abc123",
        transcript=[TranscriptSegment(text="Hello world", start=0.0, duration=2.0)],
    )


def _make_ai_response() -> AIResponse:
    return AIResponse(
        tldr="Short summary.",
        summary="Detailed summary paragraph.",
        concepts=[
            Concept(name="Concept A", definition="Definition A"),
            Concept(name="Concept B", definition="Definition B"),
        ],
    )


class TestFullPipeline:
    @patch("study.cli.ingest.create_backend")
    def test_complete_pipeline(self, mock_create_backend, tmp_path):
        mock_backend = MagicMock()
        mock_backend.process_transcript.return_value = _make_ai_response()
        mock_create_backend.return_value = mock_backend

        settings = _make_settings(tmp_path)
        storage = TranscriptStorage(settings.data_dir)
        state = ProcessingStateManager(settings.data_dir / "processing_state.json")
        results = [_make_transcript()]

        counts = _run_pipeline(results, settings, storage, state, force=False, reprocess=False)

        assert counts["transcripts_saved"] == 1
        assert counts["ai_processed"] == 1
        assert counts["notes_generated"] == 1

        # Transcript saved
        assert storage.exists("abc123")

        # AI response saved
        assert (settings.data_dir / "ai_responses" / "abc123.json").exists()

        # State fully updated
        assert state.is_transcript_extracted("abc123")
        assert state.is_ai_processed("abc123")
        assert state.is_notes_generated("abc123")

        # Vault notes created
        vault = Vault(settings.vault_path)
        assert vault.video_note_exists("abc123")
        assert vault.concept_note_exists("Concept A")
        assert vault.concept_note_exists("Concept B")

    @patch("study.cli.ingest.create_backend")
    def test_idempotent_second_run(self, mock_create_backend, tmp_path):
        mock_backend = MagicMock()
        mock_backend.process_transcript.return_value = _make_ai_response()
        mock_create_backend.return_value = mock_backend

        settings = _make_settings(tmp_path)
        storage = TranscriptStorage(settings.data_dir)
        state = ProcessingStateManager(settings.data_dir / "processing_state.json")
        results = [_make_transcript()]

        _run_pipeline(results, settings, storage, state, force=False, reprocess=False)

        # Second run should skip everything
        counts = _run_pipeline(results, settings, storage, state, force=False, reprocess=False)
        assert counts["transcripts_skipped"] == 1
        assert counts["transcripts_saved"] == 0
        assert counts["ai_processed"] == 0
        assert counts["notes_generated"] == 0

        # AI backend should only have been called once (first run)
        assert mock_backend.process_transcript.call_count == 1

    @patch("study.cli.ingest.create_backend")
    def test_partial_progress_on_ai_failure(self, mock_create_backend, tmp_path):
        mock_backend = MagicMock()
        mock_backend.process_transcript.side_effect = RuntimeError("API error")
        mock_create_backend.return_value = mock_backend

        settings = _make_settings(tmp_path)
        storage = TranscriptStorage(settings.data_dir)
        state = ProcessingStateManager(settings.data_dir / "processing_state.json")
        results = [_make_transcript()]

        counts = _run_pipeline(results, settings, storage, state, force=False, reprocess=False)

        assert counts["transcripts_saved"] == 1
        assert counts["ai_failed"] == 1
        assert counts["notes_generated"] == 0

        # Transcript was saved despite AI failure
        assert state.is_transcript_extracted("abc123")
        assert not state.is_ai_processed("abc123")
        assert not state.is_notes_generated("abc123")

    @patch("study.cli.ingest.create_backend")
    def test_shared_concept_between_videos(self, mock_create_backend, tmp_path):
        shared_concept = Concept(name="Shared Concept", definition="Shared def.")
        response1 = AIResponse(
            tldr="Video 1 tldr", summary="Video 1 summary",
            concepts=[shared_concept, Concept(name="Only in V1", definition="Def")],
        )
        response2 = AIResponse(
            tldr="Video 2 tldr", summary="Video 2 summary",
            concepts=[shared_concept, Concept(name="Only in V2", definition="Def")],
        )

        mock_backend = MagicMock()
        mock_backend.process_transcript.side_effect = [response1, response2]
        mock_create_backend.return_value = mock_backend

        settings = _make_settings(tmp_path)
        storage = TranscriptStorage(settings.data_dir)
        state = ProcessingStateManager(settings.data_dir / "processing_state.json")
        results = [
            _make_transcript("vid1", "Video One"),
            _make_transcript("vid2", "Video Two"),
        ]

        _run_pipeline(results, settings, storage, state, force=False, reprocess=False)

        vault = Vault(settings.vault_path)
        concept_path = vault.concept_note_path("Shared Concept")
        content = concept_path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(content)

        # Both videos listed as sources
        assert "[[Video One]]" in meta["sources"]
        assert "[[Video Two]]" in meta["sources"]
        assert "- [[Video One]]" in body
        assert "- [[Video Two]]" in body

    @patch("study.cli.ingest.create_backend")
    def test_force_reextracts_transcript(self, mock_create_backend, tmp_path):
        mock_backend = MagicMock()
        mock_backend.process_transcript.return_value = _make_ai_response()
        mock_create_backend.return_value = mock_backend

        settings = _make_settings(tmp_path)
        storage = TranscriptStorage(settings.data_dir)
        state = ProcessingStateManager(settings.data_dir / "processing_state.json")
        results = [_make_transcript()]

        _run_pipeline(results, settings, storage, state, force=False, reprocess=False)

        # Run with --force
        counts = _run_pipeline(results, settings, storage, state, force=True, reprocess=False)
        assert counts["transcripts_saved"] == 1
        assert counts["transcripts_skipped"] == 0

    @patch("study.cli.ingest.create_backend")
    def test_reprocess_regenerates_notes(self, mock_create_backend, tmp_path):
        mock_backend = MagicMock()
        mock_backend.process_transcript.return_value = _make_ai_response()
        mock_create_backend.return_value = mock_backend

        settings = _make_settings(tmp_path)
        storage = TranscriptStorage(settings.data_dir)
        state = ProcessingStateManager(settings.data_dir / "processing_state.json")
        results = [_make_transcript()]

        _run_pipeline(results, settings, storage, state, force=False, reprocess=False)

        # Run with --reprocess
        counts = _run_pipeline(results, settings, storage, state, force=False, reprocess=True)
        assert counts["ai_processed"] == 1
        assert counts["notes_generated"] == 1
        assert mock_backend.process_transcript.call_count == 2


class TestSaveLoadAiResponse:
    def test_roundtrip(self, tmp_path):
        response = _make_ai_response()
        path = _save_ai_response(tmp_path, "vid1", response)
        assert path.exists()

        loaded = _load_ai_response(tmp_path, "vid1")
        assert loaded is not None
        assert loaded.tldr == response.tldr
        assert loaded.summary == response.summary
        assert len(loaded.concepts) == 2
        assert loaded.concepts[0].name == "Concept A"

    def test_load_nonexistent(self, tmp_path):
        assert _load_ai_response(tmp_path, "nonexistent") is None


class TestStatusCommand:
    def test_status_empty(self, tmp_path):
        from typer.testing import CliRunner
        from study.cli.main import app

        runner = CliRunner()
        result = runner.invoke(app, ["status"], env={
            "VAULT_PATH": str(tmp_path),
            "DATA_DIR": str(tmp_path / "data"),
        })
        assert result.exit_code == 0
        assert "Transcripts:" in result.output
        assert "0 extracted" in result.output

    def test_status_with_data(self, tmp_path):
        from typer.testing import CliRunner
        from study.cli.main import app

        vault = tmp_path / "vault"
        vault.mkdir()
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        storage = TranscriptStorage(data_dir)
        state = ProcessingStateManager(data_dir / "processing_state.json")

        t = _make_transcript()
        storage.save(t)
        state.update("abc123", transcript_extracted=True, ai_processed=True)

        runner = CliRunner()
        result = runner.invoke(app, ["status"], env={
            "VAULT_PATH": str(vault),
            "DATA_DIR": str(data_dir),
        })
        assert result.exit_code == 0
        assert "1 extracted" in result.output
        assert "1 completed" in result.output


class TestConfigCommand:
    def test_config_output(self, tmp_path):
        from typer.testing import CliRunner
        from study.cli.main import app

        runner = CliRunner()
        result = runner.invoke(app, ["config"], env={
            "VAULT_PATH": str(tmp_path),
            "ANTHROPIC_API_KEY": "sk-ant-testing1234",
            "CLAUDE_BACKEND": "api",
        })
        assert result.exit_code == 0
        assert "Claude backend:" in result.output
        assert "api" in result.output
        assert "****1234" in result.output
        assert "sk-ant-testing1234" not in result.output

    def test_config_masks_short_key(self, tmp_path):
        from typer.testing import CliRunner
        from study.cli.main import app

        runner = CliRunner()
        result = runner.invoke(app, ["config"], env={
            "VAULT_PATH": str(tmp_path),
            "ANTHROPIC_API_KEY": "ab",
            "CLAUDE_BACKEND": "api",
        })
        assert result.exit_code == 0
        assert "****" in result.output
