"""
Layer 4: Output Guardrail — Validates grounding, checks for unmasked PII, and sanitizes model output.
"""

from __future__ import annotations

import re
from typing import Any

from backend.ai.firewall.data_firewall import AIDataFirewall
from backend.ai.guardrails.base import Guardrail, GuardrailLayerType, GuardrailResult


class OutputGuardrail(Guardrail):
    """
    Evaluates raw LLM generated text before delivery:
    1. Redacts sensitive PII via AIDataFirewall.
    2. Flags ungrounded claims or hallucinated execution confirmations.
    """

    def __init__(self, data_firewall: type[AIDataFirewall] = AIDataFirewall) -> None:
        self.firewall = data_firewall

    @property
    def layer_type(self) -> GuardrailLayerType:
        return GuardrailLayerType.OUTPUT

    async def evaluate(self, payload: Any, context: dict[str, Any] | None = None) -> GuardrailResult:
        text = str(payload) if payload is not None else ""
        violations: list[str] = []

        # 1. PII Redaction
        sanitized = self.firewall.sanitize_prompt(text)

        # 2. Hallucination check for authoritative mutations
        hallucination_indicators = [
            r"i\s+have\s+deleted\s+the\s+database",
            r"i\s+have\s+terminated\s+the\s+employee",
            r"i\s+have\s+transferred\s+\$[0-9,]+",
        ]
        for pattern in hallucination_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(f"Model falsely claimed execution of high-risk mutation without approval: '{pattern}'")

        passed = len(violations) == 0
        return GuardrailResult(
            passed=passed,
            layer=self.layer_type,
            violations=violations,
            risk_score=0.85 if not passed else 0.0,
            sanitized_content=sanitized if passed else None,
        )
