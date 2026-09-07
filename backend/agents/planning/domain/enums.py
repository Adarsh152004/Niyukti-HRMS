"""
Agent Planning Domain Enums — Plan and PlanStep status definitions.
"""

from __future__ import annotations

from enum import StrEnum


class PlanStatus(StrEnum):
    """Lifecycle status of an Agent Plan."""

    DRAFT = "DRAFT"
    VALIDATING = "VALIDATING"
    READY = "READY"
    EXECUTING = "EXECUTING"
    WAITING = "WAITING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    REPLANNING = "REPLANNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class StepStatus(StrEnum):
    """Lifecycle status of an individual PlanStep."""

    PENDING = "PENDING"
    READY = "READY"
    EXECUTING = "EXECUTING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"
