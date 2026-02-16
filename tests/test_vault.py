from pathlib import Path

from study.obsidian.frontmatter import serialize_frontmatter
from study.obsidian.vault import Vault


class TestVault:
    def test_ensure_structure(self, tmp_path):
        vault = Vault(tmp_path)
        vault.ensure_structure()
        assert (tmp_path / "Sources" / "YouTube").is_dir()
        assert (tmp_path / "Concepts").is_dir()

    def test_channel_dir(self, tmp_path):
        vault = Vault(tmp_path)
        path = vault.channel_dir("My Channel")
        assert path == tmp_path / "Sources" / "YouTube" / "My Channel"

    def test_video_note_path(self, tmp_path):
        vault = Vault(tmp_path)
        path = vault.video_note_path("Channel", "Video Title")
        assert path == tmp_path / "Sources" / "YouTube" / "Channel" / "Videos" / "Video Title.md"

    def test_concept_note_path(self, tmp_path):
        vault = Vault(tmp_path)
        path = vault.concept_note_path("Machine Learning")
        assert path == tmp_path / "Concepts" / "Machine Learning.md"

    def test_channel_note_path(self, tmp_path):
        vault = Vault(tmp_path)
        path = vault.channel_note_path("Tech Channel")
        assert path == tmp_path / "Sources" / "YouTube" / "Tech Channel" / "Tech Channel.md"

    def test_video_note_exists_false(self, tmp_path):
        vault = Vault(tmp_path)
        vault.ensure_structure()
        assert vault.video_note_exists("abc123") is False

    def test_video_note_exists_true(self, tmp_path):
        vault = Vault(tmp_path)
        vault.ensure_structure()
        note_dir = tmp_path / "Sources" / "YouTube" / "Ch" / "Videos"
        note_dir.mkdir(parents=True)
        fm = serialize_frontmatter({"video_id": "abc123"})
        (note_dir / "test.md").write_text(fm + "# Body\n")
        assert vault.video_note_exists("abc123") is True

    def test_concept_note_exists(self, tmp_path):
        vault = Vault(tmp_path)
        vault.ensure_structure()
        assert vault.concept_note_exists("ML") is False
        (tmp_path / "Concepts" / "ML.md").write_text("# ML\n")
        assert vault.concept_note_exists("ML") is True

    def test_sanitizes_special_chars(self, tmp_path):
        vault = Vault(tmp_path)
        path = vault.video_note_path("Ch", 'Title: "Special"')
        assert "?" not in str(path)
        assert '"' not in str(path)
