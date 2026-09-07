"""
Layer 2: Context Guardrail — Prevents context leakage, cross-tenant pollution, and unmasked secrets.
"""

from __future__ import annotations

import re
from typing import Any

from backend.ai.guardrails.base import Guardrail, GuardrailLayerType, GuardrailResult


class ContextGuardrail(Guardrail):
    """
    Evaluates assembled context prompts to ensure no cross-tenant leakage or raw credential leakage occurs.
    """

    def __init__(self) -> None:
        self.secret_patterns = [
            r"bearer\s+[a-zA-Z0-9_\-\.]{20,}",
            r"api[_-]?key\s*[:=]\s*['\"][a-zA-Z0-9_\-]{16,}['\"]",
            r"password\s*[:=]\s*['\"][^'\"]{6,}['\"]",
            r"sk-[a-zA-Z0-9]{32,}",
        ]

    @property
    def layer_type(self) -> GuardrailLayerType:
        return GuardrailLayerType.CONTEXT

    async def evaluate(self, payload: Any, context: dict[str, Any] | None = None) -> GuardrailResult:
        text = str(payload) if payload is not None else ""
        violations: list[str] = []
        ctx = context or {}

        # 1. Tenant boundary verification
        expected_tenant = ctx.get("organization_id")
        if expected_tenant and "org-" in text:
            # Detect any foreign organization IDs mentioned in context
            found_tenants = set(re.findall(r"org-[a-zA-Z0-9\-]+", text))
            foreign = [t for t in found_tenants if t != expected_tenant]
            if foreign:
                violations.append(f"Cross-tenant reference detected in context: {foreign}")

        # 2. Secret leakage detection
        for pattern in self.secret_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append("Raw API key, token, or password pattern detected in context payload.")

        passed = len(violations) == 0
        return GuardrailResult(
            passed=passed,
            layer=self.layer_type,
            violations=violations,
            risk_score=0.95 if not passed else 0.0,
            sanitized_content=payload if passed else None,
        )
