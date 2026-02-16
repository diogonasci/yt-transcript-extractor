"""Claude Code CLI backend for AI processing."""

import json
import logging
import subprocess

from study.ai.base import AIBackend
from study.ai.prompts import SYSTEM_PROMPT
from study.ai.schemas import parse_ai_response
from study.core.models import AIResponse

logger = logging.getLogger("study")

MAX_RETRIES = 2


class ClaudeCliBackend(AIBackend):
    """AI backend using the Claude Code CLI as a subprocess."""

    def process_transcript(self, transcript_text: str, video_title: str) -> AIResponse:
        """Invoke claude CLI and return structured response."""
        prompt = self._build_prompt(transcript_text, video_title)
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info("CLI call attempt %d/%d for '%s'", attempt, MAX_RETRIES, video_title)
                result = subprocess.run(
                    ["claude", "-p", full_prompt, "--output-format", "json"],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    check=False,
                )

                if result.returncode != 0:
                    raise RuntimeError(f"claude CLI exited with code {result.returncode}: {result.stderr}")

                # CLI with --output-format json wraps response in a JSON object
                output = result.stdout.strip()
                try:
                    cli_response = json.loads(output)
                    # Extract the text content from the CLI JSON wrapper
                    if isinstance(cli_response, dict) and "result" in cli_response:
                        output = cli_response["result"]
                except json.JSONDecodeError:
                    pass

                return parse_ai_response(output)
            except FileNotFoundError:
                raise RuntimeError(
                    "claude CLI not found. Install it with: npm install -g @anthropic-ai/claude-code"
                )
            except (RuntimeError, ValueError) as e:
                last_error = e
                logger.warning("Attempt %d failed: %s", attempt, e)

        raise RuntimeError(
            f"Failed to process transcript after {MAX_RETRIES} attempts: {last_error}"
        ) from last_error
