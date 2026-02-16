from study.obsidian.frontmatter import (
    parse_frontmatter,
    serialize_frontmatter,
    update_frontmatter,
)


class TestSerializeFrontmatter:
    def test_basic_dict(self):
        result = serialize_frontmatter({"type": "note", "title": "Test"})
        assert result.startswith("---\n")
        assert result.endswith("---\n")
        assert "type: note" in result
        assert "title: Test" in result

    def test_list_values(self):
        result = serialize_frontmatter({"tags": ["a", "b"]})
        assert "tags:" in result
        assert "- a" in result
        assert "- b" in result

    def test_unicode(self):
        result = serialize_frontmatter({"title": "Conceito em portugues"})
        assert "portugues" in result

    def test_empty_dict(self):
        result = serialize_frontmatter({})
        assert result == "---\n{}\n---\n"


class TestParseFrontmatter:
    def test_basic_parse(self):
        content = "---\ntype: note\ntitle: Test\n---\n# Body\n"
        meta, body = parse_frontmatter(content)
        assert meta["type"] == "note"
        assert meta["title"] == "Test"
        assert body == "# Body\n"

    def test_no_frontmatter(self):
        content = "# Just a body"
        meta, body = parse_frontmatter(content)
        assert meta == {}
        assert body == "# Just a body"

    def test_incomplete_frontmatter(self):
        content = "---\ntype: note\nno closing"
        meta, body = parse_frontmatter(content)
        assert meta == {}
        assert body == content

    def test_list_in_frontmatter(self):
        content = "---\ntags:\n  - a\n  - b\n---\nbody"
        meta, body = parse_frontmatter(content)
        assert meta["tags"] == ["a", "b"]
        assert body == "body"


class TestUpdateFrontmatter:
    def test_update_field(self):
        content = "---\ntype: note\ntitle: Old\n---\n# Body\n"
        result = update_frontmatter(content, {"title": "New"})
        meta, body = parse_frontmatter(result)
        assert meta["title"] == "New"
        assert meta["type"] == "note"
        assert body == "# Body\n"

    def test_add_new_field(self):
        content = "---\ntype: note\n---\n# Body\n"
        result = update_frontmatter(content, {"status": "done"})
        meta, _ = parse_frontmatter(result)
        assert meta["status"] == "done"
        assert meta["type"] == "note"

    def test_preserves_body(self):
        body_text = "# Title\n\nSome content here.\n"
        content = f"---\ntype: note\n---\n{body_text}"
        result = update_frontmatter(content, {"type": "updated"})
        _, body = parse_frontmatter(result)
        assert body == body_text
