"""Tests — DecisionParser and MockLLMProvider behavior."""

import pytest

from backend.agents.reasoning.application.decision_parser import DecisionParser
from backend.agents.reasoning.domain.enums import DecisionType
from backend.agents.reasoning.domain.models import LLMResponse
from backend.agents.reasoning.exceptions import InvalidDecisionError


def test_decision_parser_valid_json():
    json_str = '{"decision_type": "ANSWER", "explanation": "Done", "final_response": "Hello World"}'
    resp = LLMResponse(raw_output=json_str)

    decision = DecisionParser.parse_decision(resp)
    assert decision.decision_type == DecisionType.ANSWER
    assert decision.final_response == "Hello World"


def test_decision_parser_markdown_wrapped_json():
    markdown_json = (
        '```json\n{"decision_type": "TOOL_CALL", "selected_tool": "employee.get", "tool_arguments": {"employee_id": "e-1"}}\n```'
    )
    resp = LLMResponse(raw_output=markdown_json)

    decision = DecisionParser.parse_decision(resp)
    assert decision.decision_type == DecisionType.TOOL_CALL
    assert decision.selected_tool == "employee.get"
    assert decision.tool_arguments == {"employee_id": "e-1"}


def test_decision_parser_invalid_json_raises():
    resp = LLMResponse(raw_output="Invalid non-json text response")
    with pytest.raises(InvalidDecisionError, match="Failed to parse LLM response"):
        DecisionParser.parse_decision(resp)
