"""
Orchestration Domain Enums — State definitions and event types for Agent Orchestrator.
"""

from __future__ import annotations

from enum import StrEnum


class ExecutionState(StrEnum):
    """Execution state of an Agent Orchestrator run."""

    IDLE = "IDLE"
    PLANNING = "PLANNING"
    VALIDATING = "VALIDATING"
    EXECUTING = "EXECUTING"
    PAUSED = "PAUSED"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    REPLANNING = "REPLANNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class OrchestrationEventType(StrEnum):
    """Event types emitted during autonomous orchestration."""

    PLAN_CREATED = "hrms.agent.plan.created"
    PLAN_VALIDATED = "hrms.agent.plan.validated"
    PLAN_STARTED = "hrms.agent.plan.started"
    STEP_STARTED = "hrms.agent.step.started"
    STEP_COMPLETED = "hrms.agent.step.completed"
    STEP_FAILED = "hrms.agent.step.failed"
    WAITING_APPROVAL = "hrms.agent.waiting_approval"
    REPLANNED = "hrms.agent.replanned"
    REASONING_STARTED = "hrms.agent.reasoning.started"
    REASONING_COMPLETED = "hrms.agent.reasoning.completed"
    EXECUTION_PAUSED = "hrms.agent.execution.paused"
    EXECUTION_RESUMED = "hrms.agent.execution.resumed"
    EXECUTION_COMPLETED = "hrms.agent.execution.completed"
    EXECUTION_FAILED = "hrms.agent.execution.failed"
    LIMIT_REACHED = "hrms.agent.limit_reached"
