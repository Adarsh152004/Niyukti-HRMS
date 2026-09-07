"""
Governance Domain Enums — State definitions, evaluation types, anomaly classifications, severity tiers, containment action types, and governance decisions.
"""

from __future__ import annotations

from enum import StrEnum


class GovernanceState(StrEnum):
    """Operational governance tier for an AI Agent."""

    ACTIVE = "ACTIVE"
    MONITORED = "MONITORED"
    RESTRICTED = "RESTRICTED"
    QUARANTINED = "QUARANTINED"
    DISABLED = "DISABLED"


class ViolationType(StrEnum):
    """Classification of governance policy violations."""

    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    UNAUTHORIZED_TOOL_ATTEMPT = "UNAUTHORIZED_TOOL_ATTEMPT"
    POLICY_BYPASS_ATTEMPT = "POLICY_BYPASS_ATTEMPT"
    CROSS_TENANT_ATTEMPT = "CROSS_TENANT_ATTEMPT"
    CAPABILITY_ESCALATION_ATTEMPT = "CAPABILITY_ESCALATION_ATTEMPT"


class LedgerEventType(StrEnum):
    """Event types recorded in the immutable execution trajectory ledger."""

    REASONING_RUN = "REASONING_RUN"
    TOOL_PROPOSAL = "TOOL_PROPOSAL"
    TOOL_EXECUTION = "TOOL_EXECUTION"
    COMMAND_DISPATCH = "COMMAND_DISPATCH"
    HITL_REQUEST = "HITL_REQUEST"
    DELEGATION_GRANT = "DELEGATION_GRANT"


class EvaluationType(StrEnum):
    """Categories of agent behavioral evaluations."""

    POLICY_COMPLIANCE = "POLICY_COMPLIANCE"
    TOOL_USAGE = "TOOL_USAGE"
    COMMAND_BEHAVIOR = "COMMAND_BEHAVIOR"
    DELEGATION_BEHAVIOR = "DELEGATION_BEHAVIOR"
    TASK_SUCCESS = "TASK_SUCCESS"
    SAFETY = "SAFETY"
    PERFORMANCE = "PERFORMANCE"
    OVERALL = "OVERALL"


class EvaluationStatus(StrEnum):
    """Operational status of a trajectory evaluation."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    WARNING = "WARNING"
    FAILED = "FAILED"


class AnomalyType(StrEnum):
    """Types of detected suspicious agent behavior."""

    EXCESSIVE_TOOL_USAGE = "EXCESSIVE_TOOL_USAGE"
    REPEATED_FAILURE = "REPEATED_FAILURE"
    UNUSUAL_COMMAND_PATTERN = "UNUSUAL_COMMAND_PATTERN"
    CAPABILITY_BOUNDARY_ATTEMPT = "CAPABILITY_BOUNDARY_ATTEMPT"
    EXCESSIVE_DELEGATION = "EXCESSIVE_DELEGATION"
    RAPID_REPEATED_ACTIONS = "RAPID_REPEATED_ACTIONS"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    CROSS_TENANT_ATTEMPT = "CROSS_TENANT_ATTEMPT"
    APPROVAL_ABUSE = "APPROVAL_ABUSE"
    UNKNOWN_BEHAVIOR = "UNKNOWN_BEHAVIOR"


class Severity(StrEnum):
    """Severity classification for governance anomalies and violations."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ContainmentActionType(StrEnum):
    """Deterministic containment actions triggered upon safety violation."""

    WARN = "WARN"
    THROTTLE = "THROTTLE"
    PAUSE = "PAUSE"
    SUSPEND = "SUSPEND"
    DISABLE = "DISABLE"
    TERMINATE = "TERMINATE"


class GovernanceDecision(StrEnum):
    """Authoritative decision rendered by Governance Policy Engine."""

    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    THROTTLE = "THROTTLE"
    PAUSE = "PAUSE"
    SUSPEND = "SUSPEND"
    DENY = "DENY"
