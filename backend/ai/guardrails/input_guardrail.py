"""
Layer 1: Input Guardrail — Defends against prompt injection, jailbreaks, and untrusted inputs.
"""

from __future__ import annotations

import re
from typing import Any

from backend.ai.firewall.prompt_firewall import ContextTrustTier, PromptFirewall
from backend.ai.guardrails.base import Guardrail, GuardrailLayerType, GuardrailResult


class InputGuardrail(Guardrail):
    """
    Evaluates raw user and external data inputs for adversarial manipulation.
    Integrates PromptFirewall and regex heuristic detectors.
    """

    def __init__(self) -> None:
        self.firewall = PromptFirewall
        self.jailbreak_patterns = [
            r"ignore\s+(all\s+)?(previous\s+)?(above\s+)?instructions",
            r"disregard\s+(all\s+)?(previous\s+)?(above\s+)?(rules|instructions)",
            r"system\s+override",
            r"you\s+are\s+now\s+(in\s+)?(dan|developer)",
            r"bypass\s+security",
            r"print\s+(system\s+prompt|all\s+salaries|passwords)",
            r"reveal\s+(secret|system\s+prompt|passwords)",
            r"delete\s+all\s+records",
        ]

    @property
    def layer_type(self) -> GuardrailLayerType:
        return GuardrailLayerType.INPUT

    async def evaluate(self, payload: Any, context: dict[str, Any] | None = None) -> GuardrailResult:
        text = str(payload) if payload is not None else ""
        violations: list[str] = []

        # 1. Regex Heuristics
        for pattern in self.jailbreak_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(f"Prompt injection / jailbreak pattern detected: '{pattern}'")

        # 2. Prompt Firewall Inspection
        fw_res = self.firewall.inspect_untrusted_input(text, ContextTrustTier.USER_INPUT)
        if not fw_res.is_safe:
            violations.append(fw_res.detected_threat or "Prompt injection detected by firewall.")

        passed = len(violations) == 0
        risk_score = 0.9 if not passed else 0.05

        return GuardrailResult(
            passed=passed,
            layer=self.layer_type,
            violations=violations,
            risk_score=risk_score,
            sanitized_content=fw_res.sanitized_text if passed else None,
            metadata={"firewall_passed": fw_res.is_safe},
        )
