from study.core.models import AIResponse, Concept, TranscriptResult
from study.obsidian.frontmatter import parse_frontmatter
from study.obsidian.vault import Vault
from study.obsidian.video_note import create_video_note


def _make_transcript():
    return TranscriptResult(
        id="abc123",
        title="Test Video",
        channel="Test Channel",
        upload_date="20240115",
        webpage_url="https://youtube.com/watch?v=abc123",
    )


def _make_ai_response():
    return AIResponse(
        tldr="Short summary of the video.",
        summary="Detailed summary paragraph.",
        concepts=[
            Concept(name="Concept A", definition="Definition A"),
            Concept(name="Concept B", definition="Definition B"),
        ],
    )


class TestCreateVideoNote:
    def test_creates_note_file(self, tmp_path):
        vault = Vault(tmp_path)
        vault.ensure_structure()
        path = create_video_note(vault, _make_transcript(), _make_ai_response())
        assert path.exists()
        assert path.suffix == ".md"

    def test_frontmatter_fields(self, tmp_path):
        vault = Vault(tmp_path)
        vault.ensure_structure()
        path = create_video_note(vault, _make_transcript(), _make_ai_response())
        content = path.read_text(encoding="utf-8")
        meta, _ = parse_frontmatter(content)
        assert meta["type"] == "youtube_video"
        assert meta["video_id"] == "abc123"
        assert meta["title"] == "Test Video"
        assert meta["channel"] == "Test Channel"
        assert meta["status"] == "complete"
        assert "[[Concept A]]" in meta["concepts"]
        assert "[[Concept B]]" in meta["concepts"]

    def test_body_sections(self, tmp_path):
        vault = Vault(tmp_path)
        vault.ensure_structure()
        path = create_video_note(vault, _make_transcript(), _make_ai_response())
        content = path.read_text(encoding="utf-8")
        _, body = parse_frontmatter(content)
        assert "# Test Video" in body
        assert "## TLDR" in body
        assert "Short summary of the video." in body
        assert "## Resumo" in body
        assert "## Conceitos" in body
        assert "[[Concept A]]" in body
        assert "[[Concept B]]" in body

    def test_overwrites_existing(self, tmp_path):
        vault = Vault(tmp_path)
        vault.ensure_structure()
        path1 = create_video_note(vault, _make_transcript(), _make_ai_response())
        path2 = create_video_note(vault, _make_transcript(), _make_ai_response())
        assert path1 == path2
