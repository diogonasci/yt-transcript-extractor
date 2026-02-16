"""Tests for domain models."""

from study.core.models import (
    AIResponse,
    Concept,
    ProcessingState,
    TranscriptResult,
    TranscriptSegment,
)


class TestTranscriptResult:
    def test_full_text_concatenates(self):
        result = TranscriptResult(
            id="abc",
            title="Test",
            channel="Ch",
            upload_date="20240101",
            webpage_url="https://example.com",
            transcript=[
                TranscriptSegment(text="Hello", start=0.0, duration=1.0),
                TranscriptSegment(text="world", start=1.0, duration=1.0),
            ],
        )
        assert result.full_text == "Hello world"

    def test_full_text_empty(self):
        result = TranscriptResult(
            id="abc",
            title="Test",
            channel="Ch",
            upload_date="20240101",
            webpage_url="https://example.com",
        )
        assert result.full_text == ""

    def test_creation(self):
        seg = TranscriptSegment(text="Hi", start=0.0, duration=1.0)
        result = TranscriptResult(
            id="vid1",
            title="Title",
            channel="Channel",
            upload_date="20240101",
            webpage_url="https://example.com",
            transcript=[seg],
        )
        assert result.id == "vid1"
        assert len(result.transcript) == 1


class TestAIResponse:
    def test_creation(self):
        resp = AIResponse(
            tldr="Short summary",
            summary="Long summary",
            concepts=[Concept(name="X", definition="Def of X")],
        )
        assert resp.tldr == "Short summary"
        assert len(resp.concepts) == 1
        assert resp.concepts[0].name == "X"


class TestProcessingState:
    def test_defaults(self):
        state = ProcessingState(video_id="abc")
        assert state.transcript_extracted is False
        assert state.ai_processed is False
        assert state.notes_generated is False
        assert state.last_processed == ""
