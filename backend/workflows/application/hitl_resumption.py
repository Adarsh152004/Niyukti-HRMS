"""
HITL Workflow Resumption Service — Coordinates pausing workflows on approval gates and resuming execution.
"""

from __future__ import annotations

import logging
from typing import Any

from backend.hrms.domain.actor import Actor
from backend.workflows.domain.enums import WorkflowStatus
from backend.workflows.domain.models import WorkflowDefinition, WorkflowExecution

logger = logging.getLogger(__name__)


class HITLWorkflowResumptionService:
    """
    Manages suspending workflow DAG executions awaiting human approval and safely resuming once approved.
    """

    _instance: HITLWorkflowResumptionService | None = None

    def __init__(self) -> None:
        self._suspended_executions: dict[str, dict[str, Any]] = {}

    @classmethod
    def get_instance(cls) -> HITLWorkflowResumptionService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def suspend_workflow_step(
        self,
        workflow_def: WorkflowDefinition,
        execution: WorkflowExecution,
        step_id: str,
        approval_id: str,
    ) -> str:
        """Suspend execution at a human approval step and return resumption token."""
        token = f"hitl_token_{execution.execution_id}_{step_id}"
        self._suspended_executions[token] = {
            "workflow_def": workflow_def,
            "execution": execution,
            "step_id": step_id,
            "approval_id": approval_id,
        }
        logger.info(f"Suspended workflow [{execution.execution_id}] at step [{step_id}] on approval [{approval_id}]")
        return token

    def resume_workflow(
        self,
        token: str,
        approved: bool,
        approver_actor: Actor,
    ) -> dict[str, Any] | None:
        """Resume a suspended workflow DAG upon human approval decision."""
        entry = self._suspended_executions.pop(token, None)
        if not entry:
            return None

        execution: WorkflowExecution = entry["execution"]
        step_id: str = entry["step_id"]

        if approved:
            logger.info(
                f"Workflow [{execution.execution_id}] resumed successfully at step [{step_id}] by {approver_actor.actor_id}"
            )
            return {
                "execution_id": execution.execution_id,
                "step_id": step_id,
                "status": "RESUMED",
                "approved": True,
            }
        else:
            logger.warning(f"Workflow [{execution.execution_id}] rejected at step [{step_id}] by {approver_actor.actor_id}")
            execution.status = WorkflowStatus.FAILED
            return {
                "execution_id": execution.execution_id,
                "step_id": step_id,
                "status": "CANCELLED_ON_REJECTION",
                "approved": False,
            }
