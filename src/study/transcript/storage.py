"""Transcript persistence as JSON files."""

import json
from pathlib import Path

from study.core.models import TranscriptResult, TranscriptSegment
from study.core.utils import sanitize_filename
from study.transcript.parser import result_to_dict


class TranscriptStorage:
    """Manages transcript storage in data/transcripts/{channel}/{video_id}.json."""

    def __init__(self, data_dir: Path):
        self.base_dir = data_dir / "transcripts"

    def save(self, result: TranscriptResult) -> Path:
        """Save transcript as JSON. Returns path to saved file."""
        path = self.get_path(result.channel, result.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = result_to_dict(result)
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return path

    def load(self, video_id: str) -> TranscriptResult | None:
        """Load transcript by video_id. Search all channel dirs."""
        for json_file in self.base_dir.rglob("*.json"):
            if json_file.stem == video_id:
                return self._load_file(json_file)
        return None

    def exists(self, video_id: str) -> bool:
        """Check if transcript already exists."""
        if not self.base_dir.exists():
            return False
        for json_file in self.base_dir.rglob("*.json"):
            if json_file.stem == video_id:
                return True
        return False

    def list_all(self) -> list[str]:
        """Return all video_ids that have saved transcripts."""
        if not self.base_dir.exists():
            return []
        return [f.stem for f in self.base_dir.rglob("*.json")]

    def get_path(self, channel: str, video_id: str) -> Path:
        """Build the storage path for a transcript."""
        channel_dir = sanitize_filename(channel)
        return self.base_dir / channel_dir / f"{video_id}.json"

    def _load_file(self, path: Path) -> TranscriptResult:
        """Load a TranscriptResult from a JSON file."""
        data = json.loads(path.read_text(encoding="utf-8"))
        segments = [
            TranscriptSegment(
                text=seg["text"],
                start=seg["start"],
                duration=seg["duration"],
            )
            for seg in data.get("transcript", [])
        ]
        return TranscriptResult(
            id=data["id"],
            title=data["title"],
            channel=data["channel"],
            upload_date=data["upload_date"],
            webpage_url=data["webpage_url"],
            transcript=segments,
        )
