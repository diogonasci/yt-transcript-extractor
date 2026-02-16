from unittest.mock import MagicMock, patch

import pytest

from study.ai.api_backend import AnthropicAPIBackend
from study.core.models import AIResponse


VALID_JSON_RESPONSE = (
    '{"tldr": "Resumo curto.", "summary": "Resumo detalhado.", '
    '"concepts": [{"name": "C1", "definition": "D1"}]}'
)


def _setup_mock_anthropic(mock_anthropic):
    mock_anthropic.APIError = Exception
    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client
    return mock_client


def _make_message(text: str) -> MagicMock:
    block = MagicMock()
    block.text = text
    msg = MagicMock()
    msg.content = [block]
    return msg


class TestAnthropicAPIBackend:
    @patch("study.ai.api_backend.anthropic")
    def test_process_transcript_success(self, mock_anthropic):
        mock_client = _setup_mock_anthropic(mock_anthropic)
        mock_client.messages.create.return_value = _make_message(VALID_JSON_RESPONSE)

        backend = AnthropicAPIBackend(api_key="test-key", model="test-model")
        result = backend.process_transcript("transcript text", "Video Title")

        assert isinstance(result, AIResponse)
        assert result.tldr == "Resumo curto."
        assert len(result.concepts) == 1

        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["model"] == "test-model"
        assert "Video Title" in call_kwargs["messages"][0]["content"]

    @patch("study.ai.api_backend.anthropic")
    @patch("study.ai.api_backend.time.sleep")
    def test_retry_on_invalid_json(self, mock_sleep, mock_anthropic):
        mock_client = _setup_mock_anthropic(mock_anthropic)
        mock_client.messages.create.side_effect = [
            _make_message("not json"),
            _make_message(VALID_JSON_RESPONSE),
        ]

        backend = AnthropicAPIBackend(api_key="test-key", model="test-model")
        result = backend.process_transcript("text", "title")

        assert isinstance(result, AIResponse)
        assert mock_client.messages.create.call_count == 2

    @patch("study.ai.api_backend.anthropic")
    @patch("study.ai.api_backend.time.sleep")
    def test_raises_after_max_retries(self, mock_sleep, mock_anthropic):
        mock_client = _setup_mock_anthropic(mock_anthropic)
        mock_client.messages.create.return_value = _make_message("not json")

        backend = AnthropicAPIBackend(api_key="test-key", model="test-model")

        with pytest.raises(RuntimeError, match="Failed to process transcript"):
            backend.process_transcript("text", "title")

        assert mock_client.messages.create.call_count == 3

    @patch("study.ai.api_backend.anthropic")
    @patch("study.ai.api_backend.time.sleep")
    def test_retry_on_api_error(self, mock_sleep, mock_anthropic):
        mock_client = _setup_mock_anthropic(mock_anthropic)

        mock_client.messages.create.side_effect = [
            Exception("rate limit"),
            _make_message(VALID_JSON_RESPONSE),
        ]

        backend = AnthropicAPIBackend(api_key="test-key", model="test-model")
        result = backend.process_transcript("text", "title")

        assert isinstance(result, AIResponse)
