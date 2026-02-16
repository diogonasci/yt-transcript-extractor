from study.core.models import Concept
from study.obsidian.concept_note import create_or_update_concept
from study.obsidian.frontmatter import parse_frontmatter
from study.obsidian.vault import Vault


class TestCreateOrUpdateConcept:
    def test_create_new_concept(self, tmp_path):
        vault = Vault(tmp_path)
        vault.ensure_structure()
        concept = Concept(name="Machine Learning", definition="A branch of AI.")
        path = create_or_update_concept(vault, concept, "Video 1")
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(content)
        assert meta["type"] == "concept"
        assert meta["name"] == "Machine Learning"
        assert "[[Video 1]]" in meta["sources"]
        assert "# Machine Learning" in body
        assert "A branch of AI." in body
        assert "- [[Video 1]]" in body

    def test_update_adds_source(self, tmp_path):
        vault = Vault(tmp_path)
        vault.ensure_structure()
        concept = Concept(name="ML", definition="Original definition.")
        create_or_update_concept(vault, concept, "Video 1")
        path = create_or_update_concept(vault, concept, "Video 2")
        content = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(content)
        assert "[[Video 1]]" in meta["sources"]
        assert "[[Video 2]]" in meta["sources"]
        assert "- [[Video 2]]" in body

    def test_does_not_overwrite_definition(self, tmp_path):
        vault = Vault(tmp_path)
        vault.ensure_structure()
        concept = Concept(name="ML", definition="Original definition.")
        create_or_update_concept(vault, concept, "Video 1")
        concept2 = Concept(name="ML", definition="New definition.")
        path = create_or_update_concept(vault, concept2, "Video 2")
        content = path.read_text(encoding="utf-8")
        _, body = parse_frontmatter(content)
        assert "Original definition." in body
        assert "New definition." not in body

    def test_does_not_duplicate_source(self, tmp_path):
        vault = Vault(tmp_path)
        vault.ensure_structure()
        concept = Concept(name="ML", definition="Def.")
        create_or_update_concept(vault, concept, "Video 1")
        create_or_update_concept(vault, concept, "Video 1")
        content = vault.concept_note_path("ML").read_text(encoding="utf-8")
        meta, body = parse_frontmatter(content)
        assert meta["sources"].count("[[Video 1]]") == 1
        assert body.count("- [[Video 1]]") == 1

    def test_bidirectional_links(self, tmp_path):
        vault = Vault(tmp_path)
        vault.ensure_structure()
        concept = Concept(name="Neural Networks", definition="Computing systems.")
        path = create_or_update_concept(vault, concept, "Deep Learning Intro")
        content = path.read_text(encoding="utf-8")
        assert "[[Deep Learning Intro]]" in content
