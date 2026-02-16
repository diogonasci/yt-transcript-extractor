"""Processing state manager for idempotent pipeline execution."""

import json
from datetime import datetime, timezone
from pathlib import Path

from study.core.models import ProcessingState


class ProcessingStateManager:
    """Manages processing state persisted as JSON."""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self._states: dict[str, ProcessingState] = {}
        self._load()

    def _load(self) -> None:
        """Load state from JSON file."""
        if not self.state_file.exists():
            return
        data = json.loads(self.state_file.read_text(encoding="utf-8"))
        for video_id, fields in data.items():
            self._states[video_id] = ProcessingState(
                video_id=video_id,
                transcript_extracted=fields.get("transcript_extracted", False),
                ai_processed=fields.get("ai_processed", False),
                notes_generated=fields.get("notes_generated", False),
                last_processed=fields.get("last_processed", ""),
            )

    def _save(self) -> None:
        """Persist state to JSON file."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        for video_id, state in self._states.items():
            data[video_id] = {
                "transcript_extracted": state.transcript_extracted,
                "ai_processed": state.ai_processed,
                "notes_generated": state.notes_generated,
                "last_processed": state.last_processed,
            }
        self.state_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def get(self, video_id: str) -> ProcessingState | None:
        """Get processing state for a video."""
        return self._states.get(video_id)

    def update(self, video_id: str, **kwargs) -> None:
        """Update state fields for a video and persist."""
        if video_id not in self._states:
            self._states[video_id] = ProcessingState(video_id=video_id)
        state = self._states[video_id]
        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)
        state.last_processed = datetime.now(timezone.utc).isoformat()
        self._save()

    def is_transcript_extracted(self, video_id: str) -> bool:
        state = self._states.get(video_id)
        return state.transcript_extracted if state else False

    def is_ai_processed(self, video_id: str) -> bool:
        state = self._states.get(video_id)
        return state.ai_processed if state else False

    def is_notes_generated(self, video_id: str) -> bool:
        state = self._states.get(video_id)
        return state.notes_generated if state else False

    def pending_ai_processing(self) -> list[str]:
        """Return video_ids with transcript but not yet AI processed."""
        return [
            vid
            for vid, state in self._states.items()
            if state.transcript_extracted and not state.ai_processed
        ]
