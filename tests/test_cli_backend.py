from unittest.mock import MagicMock, patch

import pytest

from study.ai.cli_backend import ClaudeCliBackend
from study.core.models import AIResponse


VALID_JSON_RESPONSE = (
    '{"tldr": "Resumo curto.", "summary": "Resumo detalhado.", '
    '"concepts": [{"name": "C1", "definition": "D1"}]}'
)


class TestClaudeCliBackend:
    @patch("study.ai.cli_backend.subprocess.run")
    def test_process_transcript_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=VALID_JSON_RESPONSE,
            stderr="",
        )

        backend = ClaudeCliBackend()
        result = backend.process_transcript("transcript text", "Video Title")

        assert isinstance(result, AIResponse)
        assert result.tldr == "Resumo curto."
        assert len(result.concepts) == 1

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "claude"
        assert "-p" in args

    @patch("study.ai.cli_backend.subprocess.run")
    def test_handles_cli_json_wrapper(self, mock_run):
        import json
        wrapped = json.dumps({"result": VALID_JSON_RESPONSE})
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=wrapped,
            stderr="",
        )

        backend = ClaudeCliBackend()
        result = backend.process_transcript("text", "title")

        assert isinstance(result, AIResponse)

    @patch("study.ai.cli_backend.subprocess.run")
    def test_retry_on_failure(self, mock_run):
        mock_run.side_effect = [
            MagicMock(returncode=1, stdout="", stderr="error"),
            MagicMock(returncode=0, stdout=VALID_JSON_RESPONSE, stderr=""),
        ]

        backend = ClaudeCliBackend()
        result = backend.process_transcript("text", "title")

        assert isinstance(result, AIResponse)
        assert mock_run.call_count == 2

    @patch("study.ai.cli_backend.subprocess.run")
    def test_raises_after_max_retries(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")

        backend = ClaudeCliBackend()

        with pytest.raises(RuntimeError, match="Failed to process transcript"):
            backend.process_transcript("text", "title")

        assert mock_run.call_count == 2

    @patch("study.ai.cli_backend.subprocess.run", side_effect=FileNotFoundError)
    def test_raises_when_cli_not_found(self, mock_run):
        backend = ClaudeCliBackend()

        with pytest.raises(RuntimeError, match="claude CLI not found"):
            backend.process_transcript("text", "title")
