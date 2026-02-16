"""Tests for processing state manager."""

import json
from pathlib import Path

from study.core.state import ProcessingStateManager


class TestProcessingStateManager:
    def test_create_and_read(self, tmp_path: Path):
        state_file = tmp_path / "state.json"
        mgr = ProcessingStateManager(state_file)

        mgr.update("vid1", transcript_extracted=True)
        state = mgr.get("vid1")
        assert state is not None
        assert state.transcript_extracted is True
        assert state.ai_processed is False

    def test_persists_to_file(self, tmp_path: Path):
        state_file = tmp_path / "state.json"
        mgr = ProcessingStateManager(state_file)
        mgr.update("vid1", transcript_extracted=True)

        assert state_file.exists()
        data = json.loads(state_file.read_text())
        assert data["vid1"]["transcript_extracted"] is True

    def test_survives_restart(self, tmp_path: Path):
        state_file = tmp_path / "state.json"
        mgr1 = ProcessingStateManager(state_file)
        mgr1.update("vid1", transcript_extracted=True, ai_processed=True)

        mgr2 = ProcessingStateManager(state_file)
        state = mgr2.get("vid1")
        assert state is not None
        assert state.transcript_extracted is True
        assert state.ai_processed is True

    def test_update_partial(self, tmp_path: Path):
        state_file = tmp_path / "state.json"
        mgr = ProcessingStateManager(state_file)
        mgr.update("vid1", transcript_extracted=True)
        mgr.update("vid1", ai_processed=True)

        state = mgr.get("vid1")
        assert state.transcript_extracted is True
        assert state.ai_processed is True

    def test_get_nonexistent(self, tmp_path: Path):
        state_file = tmp_path / "state.json"
        mgr = ProcessingStateManager(state_file)
        assert mgr.get("nonexistent") is None

    def test_is_helpers(self, tmp_path: Path):
        state_file = tmp_path / "state.json"
        mgr = ProcessingStateManager(state_file)
        mgr.update("vid1", transcript_extracted=True)

        assert mgr.is_transcript_extracted("vid1") is True
        assert mgr.is_ai_processed("vid1") is False
        assert mgr.is_notes_generated("vid1") is False
        assert mgr.is_transcript_extracted("unknown") is False

    def test_pending_ai_processing(self, tmp_path: Path):
        state_file = tmp_path / "state.json"
        mgr = ProcessingStateManager(state_file)
        mgr.update("vid1", transcript_extracted=True)
        mgr.update("vid2", transcript_extracted=True, ai_processed=True)
        mgr.update("vid3", transcript_extracted=True)

        pending = mgr.pending_ai_processing()
        assert sorted(pending) == ["vid1", "vid3"]

    def test_creates_parent_dirs(self, tmp_path: Path):
        state_file = tmp_path / "nested" / "dir" / "state.json"
        mgr = ProcessingStateManager(state_file)
        mgr.update("vid1", transcript_extracted=True)
        assert state_file.exists()
