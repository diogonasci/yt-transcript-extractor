"""Domain models used across the project."""

from dataclasses import dataclass, field


@dataclass
class TranscriptSegment:
    """A single segment of a transcript."""

    text: str
    start: float
    duration: float


@dataclass
class TranscriptResult:
    """Complete transcript with video metadata."""

    id: str
    title: str
    channel: str
    upload_date: str
    webpage_url: str
    transcript: list[TranscriptSegment] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        """Concatenated transcript text for AI processing."""
        return " ".join(seg.text for seg in self.transcript)


@dataclass
class Concept:
    """A knowledge concept extracted by AI."""

    name: str
    definition: str


@dataclass
class AIResponse:
    """Structured response from AI processing."""

    tldr: str
    summary: str
    concepts: list[Concept] = field(default_factory=list)


@dataclass
class ProcessingState:
    """Processing state for a single video."""

    video_id: str
    transcript_extracted: bool = False
    ai_processed: bool = False
    notes_generated: bool = False
    last_processed: str = ""
