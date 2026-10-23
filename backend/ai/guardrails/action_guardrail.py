"""
Layer 5: Action Guardrail — Evaluates command risks, ensures CommandBus boundary, and routes to HITL.
"""

from __future__ import annotations

from typing import Any

from backend.ai.guardrails.base import Guardrail, GuardrailLayerType, GuardrailResult
from backend.governance.risk import RiskLevel


class ActionGuardrail(Guardrail):
    """
    Evaluates actions proposed by agents to ensure they do not perform unauthorized mutations.
    Enforces mandatory Human-In-The-Loop (HITL) for high-risk operations.
    """

    HIGH_RISK_KEYWORDS = ["terminate", "salary", "bonus", "demote", "delete", "purge", "revoke", "role_reassign"]

    @property
    def layer_type(self) -> GuardrailLayerType:
        return GuardrailLayerType.ACTION

    async def evaluate(self, payload: Any, context: dict[str, Any] | None = None) -> GuardrailResult:
        action_name = str(payload).lower() if payload is not None else ""
        violations: list[str] = []
        requires_hitl = False
        risk_level = RiskLevel.LOW

        for kw in self.HIGH_RISK_KEYWORDS:
            if kw in action_name:
                requires_hitl = True
                risk_level = RiskLevel.HIGH
                break

        # Action is allowed to proceed to CommandBus, but flagged with HITL requirement if high risk
        return GuardrailResult(
            passed=True,
            layer=self.layer_type,
            violations=violations,
            risk_score=0.9 if requires_hitl else 0.1,
            sanitized_content=payload,
            metadata={"requires_hitl": requires_hitl, "risk_level": risk_level.value},
        )
