"""
Guardrail Stack — Master orchestrator running the 6-Layer Defense-In-Depth Security Stack.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from backend.ai.guardrails.action_guardrail import ActionGuardrail
from backend.ai.guardrails.base import GuardrailLayerType, GuardrailResult
from backend.ai.guardrails.context_guardrail import ContextGuardrail
from backend.ai.guardrails.input_guardrail import InputGuardrail
from backend.ai.guardrails.output_guardrail import OutputGuardrail
from backend.ai.guardrails.runtime_guardrail import RuntimeGuardrail
from backend.ai.guardrails.tool_guardrail import ToolGuardrail

logger = logging.getLogger(__name__)


@dataclass
class StackEvaluationResult:
    """Consolidated outcome across all 6 guardrail evaluations."""

    passed: bool
    layer_results: dict[GuardrailLayerType, GuardrailResult] = field(default_factory=dict)
    all_violations: list[str] = field(default_factory=list)
    highest_risk_score: float = 0.0


class GuardrailStack:
    """
    Coordinates evaluation across the 6 defense layers:
    1. Input Guardrail
    2. Context Guardrail
    3. Tool Guardrail
    4. Output Guardrail
    5. Action Guardrail
    6. Runtime Guardrail
    """

    _instance: GuardrailStack | None = None

    def __init__(self) -> None:
        self.input_guardrail = InputGuardrail()
        self.context_guardrail = ContextGuardrail()
        self.tool_guardrail = ToolGuardrail()
        self.output_guardrail = OutputGuardrail()
        self.action_guardrail = ActionGuardrail()
        self.runtime_guardrail = RuntimeGuardrail()

    @classmethod
    def get_instance(cls) -> GuardrailStack:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def evaluate_input(self, text: str, context: dict[str, Any] | None = None) -> GuardrailResult:
        return await self.input_guardrail.evaluate(text, context)

    async def evaluate_context(self, context_prompt: str, context: dict[str, Any] | None = None) -> GuardrailResult:
        return await self.context_guardrail.evaluate(context_prompt, context)

    async def evaluate_tool(self, tool_proposal: Any, context: dict[str, Any] | None = None) -> GuardrailResult:
        return await self.tool_guardrail.evaluate(tool_proposal, context)

    async def evaluate_output(self, generated_text: str, context: dict[str, Any] | None = None) -> GuardrailResult:
        return await self.output_guardrail.evaluate(generated_text, context)

    async def evaluate_action(self, action: Any, context: dict[str, Any] | None = None) -> GuardrailResult:
        return await self.action_guardrail.evaluate(action, context)

    async def evaluate_runtime(self, context: dict[str, Any] | None = None) -> GuardrailResult:
        return await self.runtime_guardrail.evaluate(None, context)
