"""
Decision Parser — Validates raw LLM outputs against ReasoningDecision schema.
"""

from __future__ import annotations

import json
from typing import Any

from backend.agents.reasoning.domain.models import LLMResponse, ReasoningDecision
from backend.agents.reasoning.exceptions import InvalidDecisionError


class DecisionParser:
    """
    Parses and validates raw LLM output into a Pydantic ReasoningDecision object.
    """

    @staticmethod
    def parse_decision(response: LLMResponse) -> ReasoningDecision:
        if response.parsed_decision:
            return response.parsed_decision

        try:
            cleaned = response.raw_output.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned.split("```json", 1)[1].rsplit("```", 1)[0].strip()
            elif cleaned.startswith("```"):
                cleaned = cleaned.split("```", 1)[1].rsplit("```", 1)[0].strip()

            parsed_dict: dict[str, Any] = json.loads(cleaned)
            return ReasoningDecision(**parsed_dict)
        except Exception as e:
            raise InvalidDecisionError(f"Failed to parse LLM response into ReasoningDecision: {e}") from e
