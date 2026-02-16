"""AI processing backends."""

from study.ai.api_backend import AnthropicAPIBackend
from study.ai.base import AIBackend
from study.ai.cli_backend import ClaudeCliBackend
from study.core.config import Settings


def create_backend(settings: Settings) -> AIBackend:
    """Create the appropriate AI backend based on settings."""
    if settings.claude_backend == "api":
        return AnthropicAPIBackend(settings.anthropic_api_key, settings.claude_model)
    elif settings.claude_backend == "cli":
        return ClaudeCliBackend()
    raise ValueError(f"Unknown backend: {settings.claude_backend}")
