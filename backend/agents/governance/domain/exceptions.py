"""
Governance Domain Exceptions — Specialized exceptions for Governance, Budget, Containment, and Anomaly enforcement.
"""

from __future__ import annotations


class GovernanceError(Exception):
    """Base exception for governance domain errors."""

    pass


class GovernanceAccessDeniedError(GovernanceError):
    """Raised when access to governance records or modification is denied."""

    pass


class BudgetExceededError(GovernanceError):
    """Raised when an agent's allocated budget or quota limit is exhausted."""

    pass


class AgentQuarantinedError(GovernanceError):
    """Raised when an agent in QUARANTINED state attempts an action."""

    pass


class LedgerImmutabilityError(GovernanceError):
    """Raised when an illegal modification or deletion of ledger records is attempted."""

    pass


class ContainmentError(GovernanceError):
    """Raised when containment actions fail or illegal containment attempts occur."""

    pass


class AnomalyDetectionError(GovernanceError):
    """Raised when anomaly evaluation fails."""

    pass
