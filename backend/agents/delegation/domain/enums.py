"""
Delegation Domain Enums — State definitions and scope for Agent Delegation.
"""

from __future__ import annotations

from enum import StrEnum


class DelegationStatus(StrEnum):
    """Lifecycle status of an Agent Delegation."""

    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class DelegationScope(StrEnum):
    """Scope tier for agent capability delegation."""

    TASK_SCOPED = "TASK_SCOPED"
    RESOURCE_SCOPED = "RESOURCE_SCOPED"
    TIME_BOUND = "TIME_BOUND"
