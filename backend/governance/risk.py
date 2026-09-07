"""
Governance — Risk Level definitions.

Risk levels are used throughout the system to determine:
- whether human approval is required
- appropriate autonomy level
- audit verbosity
- notification urgency
"""

from __future__ import annotations

from enum import StrEnum


class RiskLevel(StrEnum):
    """
    Categorical risk levels for HRMS actions and AI decisions.

    Levels:
        LOW: Routine, reversible, minimal impact. Can proceed autonomously.
        MEDIUM: Moderate impact. Recommend human review.
        HIGH: Significant impact (e.g., candidate rejection, payroll change).
              Requires human approval by default.
        CRITICAL: Irreversible or organization-wide impact (e.g., employee termination,
                  policy change). Always requires CEO/HR_ADMIN approval.
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @property
    def requires_human_approval(self) -> bool:
        """Return True if this risk level mandates human approval."""
        return self in (RiskLevel.HIGH, RiskLevel.CRITICAL)

    @property
    def requires_ceo_approval(self) -> bool:
        """Return True if only CEO or HR_ADMIN can approve this action."""
        return self == RiskLevel.CRITICAL

    @property
    def numeric_score(self) -> int:
        """Numeric score for comparison (higher = riskier)."""
        return {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}[self.value]

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, RiskLevel):
            return NotImplemented
        return self.numeric_score < other.numeric_score

    def __le__(self, other: object) -> bool:
        if not isinstance(other, RiskLevel):
            return NotImplemented
        return self.numeric_score <= other.numeric_score

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, RiskLevel):
            return NotImplemented
        return self.numeric_score > other.numeric_score

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, RiskLevel):
            return NotImplemented
        return self.numeric_score >= other.numeric_score
