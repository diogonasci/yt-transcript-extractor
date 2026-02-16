"""Anthropic API backend for AI processing."""

import logging
import time

import anthropic

from study.ai.base import AIBackend
from study.ai.prompts import SYSTEM_PROMPT
from study.ai.schemas import parse_ai_response
from study.core.models import AIResponse

logger = logging.getLogger("study")

MAX_RETRIES = 3
RETRY_DELAY = 2


class AnthropicAPIBackend(AIBackend):
    """AI backend using the Anthropic Python SDK."""

    def __init__(self, api_key: str, model: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def process_transcript(self, transcript_text: str, video_title: str) -> AIResponse:
        """Send transcript to Anthropic API and return structured response."""
        prompt = self._build_prompt(transcript_text, video_title)

        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info("API call attempt %d/%d for '%s'", attempt, MAX_RETRIES, video_title)
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": prompt}],
                )
                raw_text = message.content[0].text
                return parse_ai_response(raw_text)
            except (anthropic.APIError, ValueError) as e:
                last_error = e
                logger.warning("Attempt %d failed: %s", attempt, e)
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY * attempt)

        raise RuntimeError(
            f"Failed to process transcript after {MAX_RETRIES} attempts: {last_error}"
        ) from last_error
