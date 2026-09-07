"""
Command Domain — Enums for Command Status, Channel, Policy Decision, and Risk Level.
"""

from __future__ import annotations

from enum import StrEnum


class CommandStatus(StrEnum):
    """Execution lifecycle status of a command."""

    RECEIVED = "RECEIVED"
    VALIDATING = "VALIDATING"
    AUTHORIZED = "AUTHORIZED"
    POLICY_CHECKED = "POLICY_CHECKED"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    DENIED = "DENIED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class CommandChannel(StrEnum):
    """Channels through which a command can enter the platform."""

    WEB = "WEB"
    CLI = "CLI"
    API = "API"
    WHATSAPP = "WHATSAPP"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"
    INTERNAL_SERVICE = "INTERNAL_SERVICE"


class PolicyDecision(StrEnum):
    """Outcomes from Policy Engine evaluation."""

    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class RiskLevel(StrEnum):
    """Risk classification levels for actions and commands."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @property
    def score(self) -> int:
        scores = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4,
        }
        return scores[self]

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, RiskLevel):
            return NotImplemented
        return self.score >= other.score

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, RiskLevel):
            return NotImplemented
        return self.score > other.score

    def __le__(self, other: object) -> bool:
        if not isinstance(other, RiskLevel):
            return NotImplemented
        return self.score <= other.score

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, RiskLevel):
            return NotImplemented
        return self.score < other.score
