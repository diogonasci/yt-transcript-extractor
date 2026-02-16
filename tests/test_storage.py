"""Tests for transcript storage."""

import json
from pathlib import Path

import pytest

from study.core.models import TranscriptResult, TranscriptSegment
from study.transcript.storage import TranscriptStorage


@pytest.fixture
def storage(tmp_path):
    return TranscriptStorage(tmp_path)


@pytest.fixture
def sample_result():
    return TranscriptResult(
        id="abc123",
        title="Test Video",
        channel="Test Channel",
        upload_date="20240615",
        webpage_url="https://www.youtube.com/watch?v=abc123",
        transcript=[
            TranscriptSegment(text="Hello", start=0.0, duration=1.0),
            TranscriptSegment(text="world", start=1.0, duration=1.5),
        ],
    )


class TestTranscriptStorage:
    def test_save_creates_json_file(self, storage, sample_result):
        path = storage.save(sample_result)
        assert path.exists()
        assert path.suffix == ".json"
        assert path.stem == "abc123"

    def test_save_includes_full_text(self, storage, sample_result):
        path = storage.save(sample_result)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["full_text"] == "Hello world"

    def test_save_path_uses_channel(self, storage, sample_result):
        path = storage.save(sample_result)
        assert "Test_Channel" in str(path) or "Test Channel" in str(path)

    def test_load_returns_transcript_result(self, storage, sample_result):
        storage.save(sample_result)
        loaded = storage.load("abc123")
        assert loaded is not None
        assert loaded.id == "abc123"
        assert loaded.title == "Test Video"
        assert loaded.channel == "Test Channel"
        assert len(loaded.transcript) == 2
        assert loaded.full_text == "Hello world"

    def test_load_nonexistent_returns_none(self, storage):
        assert storage.load("nonexistent") is None

    def test_exists_true(self, storage, sample_result):
        storage.save(sample_result)
        assert storage.exists("abc123") is True

    def test_exists_false(self, storage):
        assert storage.exists("nonexistent") is False

    def test_list_all_empty(self, storage):
        assert storage.list_all() == []

    def test_list_all_returns_ids(self, storage, sample_result):
        storage.save(sample_result)
        result2 = TranscriptResult(
            id="def456",
            title="Video 2",
            channel="Channel 2",
            upload_date="20240616",
            webpage_url="https://example.com",
            transcript=[],
        )
        storage.save(result2)
        ids = storage.list_all()
        assert sorted(ids) == ["abc123", "def456"]

    def test_get_path(self, storage):
        path = storage.get_path("My Channel", "vid123")
        assert path.name == "vid123.json"
        assert "My_Channel" in str(path) or "My Channel" in str(path)

    def test_save_overwrite(self, storage, sample_result):
        storage.save(sample_result)
        sample_result.title = "Updated Title"
        storage.save(sample_result)
        loaded = storage.load("abc123")
        assert loaded.title == "Updated Title"
