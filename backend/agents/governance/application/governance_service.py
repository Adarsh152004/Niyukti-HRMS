"""
Governance Service — Master Governance & Safety Control Plane Façade.
Orchestrates Policy, Audit, Metrics, Anomaly Detection, Evaluation, and Containment services.
"""

from __future__ import annotations

import logging

from backend.agents.application.agent_service import AgentService
from backend.agents.governance.application.anomaly_service import AnomalyService
from backend.agents.governance.application.audit_service import AuditService
from backend.agents.governance.application.containment_service import ContainmentService
from backend.agents.governance.application.evaluation_service import EvaluationService
from backend.agents.governance.application.execution_ledger_service import ExecutionLedgerService
from backend.agents.governance.application.metrics_service import MetricsService
from backend.agents.governance.application.policy_service import GovernancePolicyService
from backend.agents.governance.domain.enums import (
    ContainmentActionType,
    GovernanceDecision,
)
from backend.agents.governance.domain.models import (
    AgentEvaluation,
    AgentGovernancePolicy,
    ContainmentAction,
)
from backend.agents.governance.infrastructure.database.repositories import InMemoryGovernanceRepository
from backend.agents.governance.ports.repositories import GovernanceRepositoryPort
from backend.hrms.domain.actor import Actor

logger = logging.getLogger(__name__)


class GovernanceService:
    """
    Master Governance & Safety Control Plane Service.
    """

    def __init__(
        self,
        repository: GovernanceRepositoryPort | None = None,
        agent_service: AgentService | None = None,
    ) -> None:
        self.repository = repository or InMemoryGovernanceRepository()
        self.agent_service = agent_service or AgentService()

        self.policy_service = GovernancePolicyService(repository=self.repository)
        self.audit_service = AuditService(repository=self.repository)
        self.metrics_service = MetricsService(repository=self.repository)
        self.anomaly_service = AnomalyService(repository=self.repository)
        self.containment_service = ContainmentService(agent_service=self.agent_service, repository=self.repository)
        self.evaluation_service = EvaluationService(repository=self.repository)
        self.ledger_service = ExecutionLedgerService(repository=self.repository)

    async def get_governance_policy(self, organization_id: str, agent_id: str) -> AgentGovernancePolicy:
        """Get governance policy for agent."""
        return await self.policy_service.get_or_create_policy(organization_id, agent_id)

    async def evaluate_action(
        self,
        organization_id: str,
        agent_id: str,
        tool_name: str | None = None,
        command_name: str | None = None,
        risk_level: str = "LOW",
    ) -> GovernanceDecision:
        """Evaluate action against governance policy."""
        return await self.policy_service.evaluate_execution_policy(
            organization_id=organization_id,
            agent_id=agent_id,
            tool_name=tool_name,
            command_name=command_name,
            risk_level=risk_level,
        )

    async def contain_agent(
        self,
        organization_id: str,
        agent_id: str,
        action_type: ContainmentActionType,
        reason: str,
        triggered_by: Actor,
    ) -> ContainmentAction:
        """Trigger emergency containment action."""
        return await self.containment_service.execute_containment(
            organization_id=organization_id,
            agent_id=agent_id,
            action_type=action_type,
            reason=reason,
            triggered_by=triggered_by,
        )

    async def resolve_containment(
        self,
        organization_id: str,
        agent_id: str,
        containment_id: str,
        resolver_actor: Actor,
        reason: str = "Admin resolved containment",
    ) -> ContainmentAction:
        """Resolve containment action."""
        return await self.containment_service.resolve_containment(
            organization_id=organization_id,
            agent_id=agent_id,
            containment_id=containment_id,
            resolver_actor=resolver_actor,
            reason=reason,
        )

    async def evaluate_task(
        self,
        organization_id: str,
        agent_id: str,
        task_id: str,
    ) -> AgentEvaluation:
        """Evaluate task trajectory."""
        ledger_entries = await self.ledger_service.list_ledger_entries(organization_id, agent_id, task_id=task_id)
        return await self.evaluation_service.evaluate_agent_task(
            organization_id=organization_id,
            agent_id=agent_id,
            task_id=task_id,
            ledger_entries=ledger_entries,
        )
