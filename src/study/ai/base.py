"""Abstract base class for AI backends."""

from abc import ABC, abstractmethod

from study.ai.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from study.core.models import AIResponse


class AIBackend(ABC):
    """Abstract interface for AI processing backends."""

    @abstractmethod
    def process_transcript(self, transcript_text: str, video_title: str) -> AIResponse:
        """Send transcript to AI and return structured response."""

    def _build_prompt(self, transcript_text: str, video_title: str) -> str:
        """Build the user prompt for the AI."""
        return USER_PROMPT_TEMPLATE.format(
            title=video_title,
            transcript=transcript_text,
        )
