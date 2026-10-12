import pytest

from r3_agent.errors import ProviderError
from r3_agent.provider import parse_json_object


def test_json_parser_accepts_fenced_object() -> None:
    assert parse_json_object("```json\n{\"assessments\": []}\n```") == {"assessments": []}


def test_json_parser_rejects_arrays() -> None:
    with pytest.raises(ProviderError, match="JSON object"):
        parse_json_object("[]")
