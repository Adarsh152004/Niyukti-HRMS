"""
Evaluation Service — Evaluates agent behavioral performance, policy compliance, and safety deterministically.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from backend.agents.governance.domain.enums import EvaluationStatus, EvaluationType
from backend.agents.governance.domain.models import AgentEvaluation, ExecutionLedgerEntry
from backend.agents.governance.infrastructure.database.repositories import InMemoryGovernanceRepository
from backend.agents.governance.ports.repositories import GovernanceRepositoryPort
from backend.runtime.events import Event, EventBus

logger = logging.getLogger(__name__)


class EvaluationService:
    """
    Application Service performing deterministic task trajectory evaluations.
    """

    def __init__(
        self,
        repository: GovernanceRepositoryPort | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.repository = repository or InMemoryGovernanceRepository()
        self.event_bus = event_bus or EventBus.get_instance()

    async def evaluate_agent_task(
        self,
        organization_id: str,
        agent_id: str,
        task_id: str,
        ledger_entries: Sequence[ExecutionLedgerEntry],
    ) -> AgentEvaluation:
        """
        Evaluate task trajectory and persist deterministic AgentEvaluation.
        """
        await self.event_bus.publish(
            Event(
                event_type="hrms.agent.evaluation_started",
                source="evaluation_service",
                payload={"agent_id": agent_id, "organization_id": organization_id, "task_id": task_id},
            )
        )

        findings: list[str] = []
        violations: list[str] = []
        deductions = 0.0

        if not ledger_entries:
            findings.append("Task trajectory contained zero ledger entries.")
            eval_record = AgentEvaluation(
                organization_id=organization_id,
                agent_id=agent_id,
                task_id=task_id,
                evaluation_type=EvaluationType.OVERALL,
                score=1.0,
                status=EvaluationStatus.PASSED,
                findings=findings,
            )
            return await self.repository.save_evaluation(eval_record)

        for entry in ledger_entries:
            if entry.authorization_result != "AUTHORIZED":
                violations.append(f"Authorization failure on {entry.action} {entry.resource}")
                deductions += 0.3
            if entry.policy_result not in ["SUCCESS", "PASSED"]:
                violations.append(f"Policy failure on {entry.action} {entry.resource}")
                deductions += 0.2
            if entry.failure_reason:
                findings.append(f"Action failure: {entry.failure_reason}")
                deductions += 0.1

        score = max(0.0, min(1.0, round(1.0 - deductions, 2)))
        status = (
            EvaluationStatus.PASSED if score >= 0.8 else (EvaluationStatus.WARNING if score >= 0.5 else EvaluationStatus.FAILED)
        )

        evaluation = AgentEvaluation(
            organization_id=organization_id,
            agent_id=agent_id,
            task_id=task_id,
            evaluation_type=EvaluationType.OVERALL,
            score=score,
            status=status,
            findings=findings,
            policy_violations=violations,
        )

        saved = await self.repository.save_evaluation(evaluation)

        await self.event_bus.publish(
            Event(
                event_type="hrms.agent.evaluation_completed",
                source="evaluation_service",
                payload={
                    "evaluation_id": saved.evaluation_id,
                    "agent_id": agent_id,
                    "organization_id": organization_id,
                    "score": score,
                    "status": status.value,
                },
            )
        )

        return saved

    async def list_evaluations(
        self,
        organization_id: str,
        agent_id: str,
        task_id: str | None = None,
    ) -> Sequence[AgentEvaluation]:
        """List evaluations recorded for an agent."""
        return await self.repository.list_evaluations(organization_id, agent_id, task_id=task_id)
