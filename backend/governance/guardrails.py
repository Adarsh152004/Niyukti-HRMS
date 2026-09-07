"""
Governance — Safety Guardrail contracts.

Guardrails form the first defense layer before any agent action executes.
They must validate: policy compliance, permissions, input safety, risk level,
PII exposure, rate limits, and confidence thresholds.

No agent may bypass guardrails. Emergency stop supersedes all autonomy levels.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from backend.governance.risk import RiskLevel


class GuardrailResult(StrEnum):
    """Outcome of a guardrail evaluation."""

    PASS = "PASS"
    WARN = "WARN"
    BLOCK = "BLOCK"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    EMERGENCY_STOP = "EMERGENCY_STOP"


@dataclass
class GuardrailContext:
    """
    Context passed to each guardrail for evaluation.

    All fields must be sanitized — no raw PII.
    """

    agent_id: str
    agent_role: str
    action_type: str
    resource_type: str
    resource_id: str | None
    parameters: dict[str, Any]
    risk_level: RiskLevel
    actor_id: str
    actor_role: str
    channel: str
    confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GuardrailEvaluation:
    """Result of a single guardrail check."""

    guardrail_name: str
    result: GuardrailResult
    reason: str
    blocking: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GuardrailReport:
    """Aggregate report from running all guardrails on a context."""

    context: GuardrailContext
    evaluations: list[GuardrailEvaluation] = field(default_factory=list)

    @property
    def overall_result(self) -> GuardrailResult:
        """Return the most severe result across all evaluations."""
        priority = [
            GuardrailResult.EMERGENCY_STOP,
            GuardrailResult.BLOCK,
            GuardrailResult.REQUIRE_APPROVAL,
            GuardrailResult.WARN,
            GuardrailResult.PASS,
        ]
        for level in priority:
            if any(e.result == level for e in self.evaluations):
                return level
        return GuardrailResult.PASS

    @property
    def is_blocked(self) -> bool:
        return self.overall_result in (
            GuardrailResult.BLOCK,
            GuardrailResult.EMERGENCY_STOP,
        )

    @property
    def requires_approval(self) -> bool:
        return self.overall_result == GuardrailResult.REQUIRE_APPROVAL

    @property
    def blocking_reasons(self) -> list[str]:
        return [e.reason for e in self.evaluations if e.blocking]


class SafetyGuardrail(ABC):
    """
    Abstract safety guardrail.

    Each concrete guardrail checks one specific concern (policy, PII, risk, etc.).
    Guardrails are composed into a GuardrailChain and evaluated sequentially.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique guardrail name for identification in reports."""
        ...

    @abstractmethod
    async def evaluate(self, context: GuardrailContext) -> GuardrailEvaluation:
        """
        Evaluate the guardrail for the given action context.

        Must not raise exceptions — return a BLOCK evaluation instead.
        """
        ...


class PolicyValidationGuardrail(SafetyGuardrail):
    """Validates that the proposed action complies with current HR policies."""

    @property
    def name(self) -> str:
        return "policy_validation"

    async def evaluate(self, context: GuardrailContext) -> GuardrailEvaluation:
        # Placeholder — concrete implementation in later node
        return GuardrailEvaluation(
            guardrail_name=self.name,
            result=GuardrailResult.PASS,
            reason="Policy validation not yet implemented — defaulting to PASS",
        )


class RiskThresholdGuardrail(SafetyGuardrail):
    """Blocks or escalates actions whose risk level exceeds configured thresholds."""

    @property
    def name(self) -> str:
        return "risk_threshold"

    async def evaluate(self, context: GuardrailContext) -> GuardrailEvaluation:
        if context.risk_level.requires_human_approval:
            return GuardrailEvaluation(
                guardrail_name=self.name,
                result=GuardrailResult.REQUIRE_APPROVAL,
                reason=(f"Action has risk level {context.risk_level.value}, " "which requires human approval."),
                blocking=False,
            )
        return GuardrailEvaluation(
            guardrail_name=self.name,
            result=GuardrailResult.PASS,
            reason=f"Risk level {context.risk_level.value} within autonomous threshold.",
        )


class ConfidenceThresholdGuardrail(SafetyGuardrail):
    """Blocks AI actions whose confidence score falls below the minimum threshold."""

    def __init__(self, min_confidence: float = 0.7) -> None:
        self._min_confidence = min_confidence

    @property
    def name(self) -> str:
        return "confidence_threshold"

    async def evaluate(self, context: GuardrailContext) -> GuardrailEvaluation:
        if context.confidence is None:
            return GuardrailEvaluation(
                guardrail_name=self.name,
                result=GuardrailResult.WARN,
                reason="No confidence score provided — proceeding with caution.",
            )
        if context.confidence < self._min_confidence:
            return GuardrailEvaluation(
                guardrail_name=self.name,
                result=GuardrailResult.REQUIRE_APPROVAL,
                reason=(f"AI confidence {context.confidence:.2f} is below " f"minimum threshold {self._min_confidence:.2f}."),
                blocking=False,
            )
        return GuardrailEvaluation(
            guardrail_name=self.name,
            result=GuardrailResult.PASS,
            reason=f"Confidence {context.confidence:.2f} meets threshold.",
        )


class EmergencyStopGuardrail(SafetyGuardrail):
    """
    Blocks ALL autonomous agent actions when an emergency stop is active.

    The emergency stop can only be cleared by CEO or SUPER_ADMIN.
    """

    def __init__(self) -> None:
        self._active: bool = False

    @property
    def name(self) -> str:
        return "emergency_stop"

    @property
    def is_active(self) -> bool:
        return self._active

    def activate(self, reason: str = "") -> None:
        """Activate the emergency stop. All autonomous actions will be blocked."""
        self._active = True

    def deactivate(self) -> None:
        """Deactivate the emergency stop. Must only be called by authorized actors."""
        self._active = False

    async def evaluate(self, context: GuardrailContext) -> GuardrailEvaluation:
        if self._active:
            return GuardrailEvaluation(
                guardrail_name=self.name,
                result=GuardrailResult.EMERGENCY_STOP,
                reason="Emergency stop is active. All autonomous actions are suspended.",
                blocking=True,
            )
        return GuardrailEvaluation(
            guardrail_name=self.name,
            result=GuardrailResult.PASS,
            reason="Emergency stop not active.",
        )


class GuardrailChain:
    """
    Executes a sequence of safety guardrails and aggregates results.

    Guardrails are evaluated in order. Evaluation continues through all
    guardrails even if one blocks (to collect complete report).
    Emergency stop short-circuits remaining evaluations.
    """

    def __init__(self) -> None:
        self._guardrails: list[SafetyGuardrail] = []

    def add(self, guardrail: SafetyGuardrail) -> GuardrailChain:
        self._guardrails.append(guardrail)
        return self

    async def evaluate(self, context: GuardrailContext) -> GuardrailReport:
        report = GuardrailReport(context=context)
        for guardrail in self._guardrails:
            evaluation = await guardrail.evaluate(context)
            report.evaluations.append(evaluation)
            # Emergency stop short-circuits
            if evaluation.result == GuardrailResult.EMERGENCY_STOP:
                break
        return report
