"""
Layer 6: Runtime Guardrail — Prevents runaway loops, enforces step limits, timeouts, and cost bounds.
"""

from __future__ import annotations

from typing import Any

from backend.ai.guardrails.base import Guardrail, GuardrailLayerType, GuardrailResult


class RuntimeGuardrail(Guardrail):
    """
    Monitors execution state during multi-step reasoning:
    1. Maximum tool calls per task.
    2. Step execution limits.
    3. Delegation depth caps.
    4. Cost budget constraints.
    """

    def __init__(
        self,
        max_tool_calls: int = 20,
        max_steps: int = 30,
        max_delegation_depth: int = 3,
    ) -> None:
        self.max_tool_calls = max_tool_calls
        self.max_steps = max_steps
        self.max_delegation_depth = max_delegation_depth

    @property
    def layer_type(self) -> GuardrailLayerType:
        return GuardrailLayerType.RUNTIME

    async def evaluate(self, payload: Any, context: dict[str, Any] | None = None) -> GuardrailResult:
        ctx = context or {}
        violations: list[str] = []

        step_count = ctx.get("current_step", 0)
        tool_calls_count = ctx.get("tool_calls_count", 0)
        delegation_depth = ctx.get("delegation_depth", 0)
        cost_usd = ctx.get("current_cost_usd", 0.0)
        budget_usd = ctx.get("daily_budget_usd", 20.0)

        if step_count > self.max_steps:
            violations.append(f"Maximum reasoning step limit ({self.max_steps}) exceeded: {step_count}")

        if tool_calls_count > self.max_tool_calls:
            violations.append(f"Maximum tool call limit ({self.max_tool_calls}) exceeded: {tool_calls_count}")

        if delegation_depth > self.max_delegation_depth:
            violations.append(f"Maximum delegation depth ({self.max_delegation_depth}) exceeded: {delegation_depth}")

        if cost_usd > budget_usd:
            violations.append(f"Agent budget exhausted: ${cost_usd:.2f} >= ${budget_usd:.2f}")

        passed = len(violations) == 0
        return GuardrailResult(
            passed=passed,
            layer=self.layer_type,
            violations=violations,
            risk_score=1.0 if not passed else 0.0,
            metadata={"step_count": step_count, "cost_usd": cost_usd},
        )
