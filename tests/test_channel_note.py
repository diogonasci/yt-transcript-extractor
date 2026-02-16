from study.obsidian.channel_note import create_or_update_channel
from study.obsidian.frontmatter import parse_frontmatter
from study.obsidian.vault import Vault


class TestCreateOrUpdateChannel:
    def test_create_new_channel(self, tmp_path):
        vault = Vault(tmp_path)
        vault.ensure_structure()
        path = create_or_update_channel(vault, "Tech Channel", "https://youtube.com/@tech", "Video 1")
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(content)
        assert meta["type"] == "youtube_channel"
        assert meta["name"] == "Tech Channel"
        assert meta["url"] == "https://youtube.com/@tech"
        assert "youtube" in meta["tags"]
        assert "channel" in meta["tags"]
        assert "# Tech Channel" in body
        assert "- [[Video 1]]" in body

    def test_update_adds_video(self, tmp_path):
        vault = Vault(tmp_path)
        vault.ensure_structure()
        create_or_update_channel(vault, "Ch", "https://yt.com/@ch", "Video 1")
        path = create_or_update_channel(vault, "Ch", "https://yt.com/@ch", "Video 2")
        content = path.read_text(encoding="utf-8")
        _, body = parse_frontmatter(content)
        assert "- [[Video 1]]" in body
        assert "- [[Video 2]]" in body

    def test_does_not_duplicate_video(self, tmp_path):
        vault = Vault(tmp_path)
        vault.ensure_structure()
        create_or_update_channel(vault, "Ch", "https://yt.com/@ch", "Video 1")
        create_or_update_channel(vault, "Ch", "https://yt.com/@ch", "Video 1")
        content = vault.channel_note_path("Ch").read_text(encoding="utf-8")
        assert content.count("- [[Video 1]]") == 1

    def test_updates_timestamp(self, tmp_path):
        vault = Vault(tmp_path)
        vault.ensure_structure()
        create_or_update_channel(vault, "Ch", "https://yt.com/@ch", "Video 1")
        path = vault.channel_note_path("Ch")
        meta1, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        create_or_update_channel(vault, "Ch", "https://yt.com/@ch", "Video 2")
        meta2, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        assert meta2["updated"] >= meta1["created"]
