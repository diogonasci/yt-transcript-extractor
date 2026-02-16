import pytest

from study.ai.schemas import parse_ai_response, validate_ai_response
from study.core.models import AIResponse


VALID_RESPONSE = {
    "tldr": "Resumo curto do video.",
    "summary": "Resumo detalhado em markdown.",
    "concepts": [
        {"name": "Conceito A", "definition": "Definicao A"},
        {"name": "Conceito B", "definition": "Definicao B"},
    ],
}

VALID_JSON = (
    '{"tldr": "Resumo curto.", "summary": "Resumo detalhado.", '
    '"concepts": [{"name": "C1", "definition": "D1"}]}'
)


class TestValidateAiResponse:
    def test_valid_response(self):
        result = validate_ai_response(VALID_RESPONSE)
        assert isinstance(result, AIResponse)
        assert result.tldr == "Resumo curto do video."
        assert len(result.concepts) == 2
        assert result.concepts[0].name == "Conceito A"

    def test_missing_tldr(self):
        data = {"summary": "s", "concepts": []}
        with pytest.raises(ValueError, match="Missing required field: tldr"):
            validate_ai_response(data)

    def test_missing_summary(self):
        data = {"tldr": "t", "concepts": []}
        with pytest.raises(ValueError, match="Missing required field: summary"):
            validate_ai_response(data)

    def test_missing_concepts(self):
        data = {"tldr": "t", "summary": "s"}
        with pytest.raises(ValueError, match="Missing required field: concepts"):
            validate_ai_response(data)

    def test_concepts_not_list(self):
        data = {"tldr": "t", "summary": "s", "concepts": "not a list"}
        with pytest.raises(ValueError, match="must be a list"):
            validate_ai_response(data)

    def test_concept_missing_name(self):
        data = {"tldr": "t", "summary": "s", "concepts": [{"definition": "d"}]}
        with pytest.raises(ValueError, match="missing 'name' or 'definition'"):
            validate_ai_response(data)

    def test_concept_missing_definition(self):
        data = {"tldr": "t", "summary": "s", "concepts": [{"name": "n"}]}
        with pytest.raises(ValueError, match="missing 'name' or 'definition'"):
            validate_ai_response(data)

    def test_not_a_dict(self):
        with pytest.raises(ValueError, match="must be a JSON object"):
            validate_ai_response("not a dict")

    def test_empty_concepts_list(self):
        data = {"tldr": "t", "summary": "s", "concepts": []}
        result = validate_ai_response(data)
        assert result.concepts == []


class TestParseAiResponse:
    def test_plain_json(self):
        result = parse_ai_response(VALID_JSON)
        assert isinstance(result, AIResponse)
        assert result.tldr == "Resumo curto."

    def test_json_with_code_fences(self):
        raw = f"```json\n{VALID_JSON}\n```"
        result = parse_ai_response(raw)
        assert result.tldr == "Resumo curto."

    def test_json_with_plain_fences(self):
        raw = f"```\n{VALID_JSON}\n```"
        result = parse_ai_response(raw)
        assert result.tldr == "Resumo curto."

    def test_invalid_json(self):
        with pytest.raises(ValueError, match="Invalid JSON"):
            parse_ai_response("not json at all")

    def test_valid_json_but_missing_fields(self):
        with pytest.raises(ValueError, match="Missing required field"):
            parse_ai_response('{"tldr": "t"}')
