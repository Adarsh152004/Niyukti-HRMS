"""
Agent Domain — Enums for Agent Types, Lifecycle Statuses, Task Statuses, and Task Priorities.
"""

from __future__ import annotations

from enum import StrEnum


class AgentType(StrEnum):
    """Business classifications describing an AI Agent's domain responsibility."""

    SYSTEM_AGENT = "SYSTEM_AGENT"
    HR_AGENT = "HR_AGENT"
    RECRUITMENT_AGENT = "RECRUITMENT_AGENT"
    ONBOARDING_AGENT = "ONBOARDING_AGENT"
    EMPLOYEE_SUPPORT_AGENT = "EMPLOYEE_SUPPORT_AGENT"
    PAYROLL_AGENT = "PAYROLL_AGENT"
    COMPLIANCE_AGENT = "COMPLIANCE_AGENT"
    ANALYTICS_AGENT = "ANALYTICS_AGENT"
    WORKFLOW_AGENT = "WORKFLOW_AGENT"
    EXECUTIVE_AGENT = "EXECUTIVE_AGENT"
    CUSTOM_AGENT = "CUSTOM_AGENT"


class AgentStatus(StrEnum):
    """Lifecycle status of an AI Agent."""

    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    SUSPENDED = "SUSPENDED"
    DRAINING = "DRAINING"
    DISABLED = "DISABLED"
    TERMINATED = "TERMINATED"


class TaskStatus(StrEnum):
    """Execution status of an Agent Task."""

    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    DELEGATED = "DELEGATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class TaskPriority(StrEnum):
    """Agent Task execution priority."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
