"""
Workflow Domain — Enums for Workflow Status, Step Status, Triggers, Execution, Retry, and Priority.
"""

from __future__ import annotations

from enum import StrEnum


class WorkflowStatus(StrEnum):
    """Lifecycle status of a workflow definition or instance."""

    DRAFT = "DRAFT"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    PAUSED = "PAUSED"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class StepStatus(StrEnum):
    """Execution status of an individual workflow step."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"


class TriggerType(StrEnum):
    """Triggers that start a workflow execution."""

    MANUAL = "MANUAL"
    COMMAND = "COMMAND"
    EVENT = "EVENT"
    CRON = "CRON"
    DELAY = "DELAY"
    WEBHOOK = "WEBHOOK"


class ExecutionStatus(StrEnum):
    """Durable job execution status in queue."""

    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    DEAD_LETTER = "DEAD_LETTER"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"


class RetryStrategy(StrEnum):
    """Retry policy backoff strategy."""

    NONE = "NONE"
    FIXED = "FIXED"
    EXPONENTIAL = "EXPONENTIAL"
    EXPONENTIAL_JITTER = "EXPONENTIAL_JITTER"


class Priority(StrEnum):
    """Execution priority levels."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    MEDIUM = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ErrorCategory(StrEnum):
    """Error categories for retry engine decision making."""

    RETRYABLE = "RETRYABLE"
    NON_RETRYABLE = "NON_RETRYABLE"
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    VALIDATION = "VALIDATION"
    CONFLICT = "CONFLICT"
    RATE_LIMITED = "RATE_LIMITED"
    TIMEOUT = "TIMEOUT"
    INFRASTRUCTURE = "INFRASTRUCTURE"
