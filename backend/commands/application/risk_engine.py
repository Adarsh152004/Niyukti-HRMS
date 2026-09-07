"""
Risk Engine — Classifies commands and actions into risk levels (LOW, MEDIUM, HIGH, CRITICAL).
"""

from __future__ import annotations

from backend.commands.domain.enums import RiskLevel
from backend.commands.domain.models import Command, RiskAssessment


class RiskEngine:
    """
    Evaluates action risk classification.
    """

    def __init__(self) -> None:
        self._type_risk_overrides: dict[str, RiskLevel] = {}

    def set_risk_override(self, command_type: str, risk_level: RiskLevel) -> None:
        """Register explicit risk override for a command type."""
        self._type_risk_overrides[command_type.lower()] = risk_level

    def assess_risk(self, command: Command) -> RiskAssessment:
        """
        Assess risk level for a command instance.
        """
        cmd_type_lower = command.command_type.lower()

        # 1. Check explicit override map
        if cmd_type_lower in self._type_risk_overrides:
            lvl = self._type_risk_overrides[cmd_type_lower]
            return RiskAssessment(
                risk_level=lvl,
                score=lvl.score,
                reasons=[f"Explicit risk override set for '{command.command_type}'"],
            )

        # 2. Heuristic risk classification
        if any(term in cmd_type_lower for term in ["delete_organization", "grant_admin", "purge"]):
            return RiskAssessment(
                risk_level=RiskLevel.CRITICAL,
                score=RiskLevel.CRITICAL.score,
                reasons=["Critical system operation affecting organization data or security grants"],
            )

        if any(term in cmd_type_lower for term in ["terminate", "salary", "delete", "revoke_agent"]):
            return RiskAssessment(
                risk_level=RiskLevel.HIGH,
                score=RiskLevel.HIGH.score,
                reasons=["High risk action affecting personnel status or financial data"],
            )

        if any(term in cmd_type_lower for term in ["create", "update", "upload"]):
            return RiskAssessment(
                risk_level=RiskLevel.MEDIUM,
                score=RiskLevel.MEDIUM.score,
                reasons=["Medium risk mutation operation"],
            )

        return RiskAssessment(
            risk_level=RiskLevel.LOW,
            score=RiskLevel.LOW.score,
            reasons=["Low risk read or informational operation"],
        )
