"""Tests for CLI commands using typer CliRunner."""

from typer.testing import CliRunner

from study.cli.main import app

runner = CliRunner()


class TestCLI:
    def test_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "YouTube" in result.output

    def test_status(self):
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "not implemented yet" in result.output

    def test_config(self):
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "not implemented yet" in result.output


class TestIngestCLI:
    def test_help(self):
        result = runner.invoke(app, ["ingest", "--help"])
        assert result.exit_code == 0
        assert "video" in result.output
        assert "playlist" in result.output
        assert "channel" in result.output

    def test_video_stub(self):
        result = runner.invoke(app, ["ingest", "video", "https://example.com"])
        assert result.exit_code == 0
        assert "not implemented yet" in result.output

    def test_playlist_stub(self):
        result = runner.invoke(app, ["ingest", "playlist", "https://example.com"])
        assert result.exit_code == 0

    def test_channel_stub(self):
        result = runner.invoke(app, ["ingest", "channel", "https://example.com"])
        assert result.exit_code == 0


class TestTranscriptCLI:
    def test_help(self):
        result = runner.invoke(app, ["transcript", "--help"])
        assert result.exit_code == 0
        assert "video" in result.output
        assert "playlist" in result.output
        assert "channel" in result.output

    def test_video_help(self):
        result = runner.invoke(app, ["transcript", "video", "--help"])
        assert result.exit_code == 0
        assert "url" in result.output.lower() or "URL" in result.output


class TestProcessCLI:
    def test_help(self):
        result = runner.invoke(app, ["process", "--help"])
        assert result.exit_code == 0

    def test_run_single(self):
        result = runner.invoke(app, ["process", "run", "abc123"])
        assert result.exit_code == 0
        assert "abc123" in result.output

    def test_run_all(self):
        result = runner.invoke(app, ["process", "run", "--all"])
        assert result.exit_code == 0
