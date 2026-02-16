"""Validation and parsing for AI response JSON."""

import json
import re

from study.core.models import AIResponse, Concept


def validate_ai_response(data: dict) -> AIResponse:
    """Validate and parse AI response dict into AIResponse."""
    if not isinstance(data, dict):
        raise ValueError("AI response must be a JSON object")

    for field in ("tldr", "summary", "concepts"):
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    if not isinstance(data["tldr"], str):
        raise ValueError("Field 'tldr' must be a string")
    if not isinstance(data["summary"], str):
        raise ValueError("Field 'summary' must be a string")
    if not isinstance(data["concepts"], list):
        raise ValueError("Field 'concepts' must be a list")

    concepts = []
    for i, item in enumerate(data["concepts"]):
        if not isinstance(item, dict):
            raise ValueError(f"Concept at index {i} must be an object")
        if "name" not in item or "definition" not in item:
            raise ValueError(f"Concept at index {i} missing 'name' or 'definition'")
        concepts.append(Concept(name=item["name"], definition=item["definition"]))

    return AIResponse(
        tldr=data["tldr"],
        summary=data["summary"],
        concepts=concepts,
    )


def parse_ai_response(raw_text: str) -> AIResponse:
    """Parse raw text response (possibly with markdown fences) into AIResponse."""
    text = raw_text.strip()

    # Strip markdown code fences if present
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if match:
        text = match.group(1).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in AI response: {e}") from e

    return validate_ai_response(data)
