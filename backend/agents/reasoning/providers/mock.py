"""
Mock LLM Provider — Deterministic provider implementation for automated testing.
"""

from __future__ import annotations

import json
from typing import Any

from backend.agents.reasoning.domain.enums import DecisionType
from backend.agents.reasoning.domain.models import LLMRequest, LLMResponse, ReasoningDecision
from backend.agents.reasoning.exceptions import LLMProviderError
from backend.agents.reasoning.providers.base import LLMProviderPort


class MockLLMProvider(LLMProviderPort):
    """
    Deterministic Mock LLM provider for unit and integration testing.
    """

    def __init__(self, responses: list[dict[str, Any]] | None = None) -> None:
        self.responses = responses or []
        self._step_counter = 0
        self.simulate_timeout = False
        self.simulate_failure = False

    def enqueue_decision(self, decision: ReasoningDecision) -> None:
        """Enqueue a structured decision."""
        self.responses.append(decision.model_dump())

    def enqueue_raw_json(self, raw_json: str) -> None:
        """Enqueue raw JSON response string."""
        self.responses.append({"__raw__": raw_json})

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate deterministic response."""
        if self.simulate_failure:
            raise LLMProviderError("Simulated LLM Provider failure.")

        if self.simulate_timeout:
            raise LLMProviderError("Simulated LLM Provider timeout.")

        if self._step_counter < len(self.responses):
            resp_data = self.responses[self._step_counter]
            self._step_counter += 1
        else:
            # Default fallback response if queue exhausted
            resp_data = ReasoningDecision(
                decision_type=DecisionType.ANSWER,
                explanation="Default mock response.",
                final_response="Completed default response.",
            ).model_dump()

        if "__raw__" in resp_data:
            raw_str = resp_data["__raw__"]
            return LLMResponse(raw_output=raw_str, parsed_decision=None)

        decision = ReasoningDecision(**resp_data)
        raw_json_str = json.dumps(resp_data)
        return LLMResponse(raw_output=raw_json_str, parsed_decision=decision)
