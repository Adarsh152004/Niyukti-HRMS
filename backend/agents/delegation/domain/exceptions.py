"""
Delegation Domain Exceptions — Specialized exception hierarchy for Multi-Agent Delegation.
"""

from __future__ import annotations


class DelegationError(Exception):
    """Base exception for delegation domain errors."""

    pass


class DelegationAccessDeniedError(DelegationError):
    """Raised when delegation access or capability check fails."""

    pass


class DelegationValidationError(DelegationError):
    """Raised when delegation structural or policy validation fails."""

    pass


class DelegationExpiredError(DelegationError):
    """Raised when an attempt is made to execute an expired delegation."""

    pass


class PrivilegeEscalationError(DelegationError):
    """Raised when a delegation attempts to grant capabilities broader than delegator possesses."""

    pass


class RecursiveDelegationDeniedError(DelegationError):
    """Raised when recursive delegation is disallowed by policy."""

    pass
