"""
SupervisorAgent — High-level Supervisor / Worker pattern orchestration engine.
Coordinates multi-agent task breakdown, worker discovery, delegation execution, and result aggregation.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Any

from backend.agents.application.agent_service import AgentService
from backend.agents.delegation.application.delegation_executor import DelegationExecutor
from backend.agents.delegation.application.delegation_service import DelegationService
from backend.agents.delegation.domain.models import DelegatedTask, Delegation
from backend.agents.domain.enums import AgentStatus
from backend.agents.domain.models import Agent, AgentCapability

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """
    Supervisor Agent pattern interface managing worker discovery, task delegation, monitoring, and result aggregation.
    """

    def __init__(
        self,
        agent_service: AgentService | None = None,
        delegation_service: DelegationService | None = None,
        executor: DelegationExecutor | None = None,
    ) -> None:
        self.agent_service = agent_service or AgentService()
        self.delegation_service = delegation_service or DelegationService(agent_service=self.agent_service)
        self.executor = executor or DelegationExecutor(
            delegation_service=self.delegation_service,
            agent_service=self.agent_service,
        )

    async def discover_eligible_workers(
        self,
        organization_id: str,
        resource: str,
        actions: list[str],
    ) -> Sequence[Agent]:
        """
        Discover active agents in tenant possessing capabilities covering target resource and actions.
        """
        all_agents = await self.agent_service.list_agents(organization_id)
        eligible: list[Agent] = []

        for agent in all_agents:
            if agent.status != AgentStatus.ACTIVE:
                continue
            has_cap = any(
                c.enabled and c.resource == resource and set(actions).issubset(set(c.actions)) for c in agent.capabilities
            )
            if has_cap:
                eligible.append(agent)

        return eligible

    async def delegate_subtask(
        self,
        organization_id: str,
        supervisor_agent_id: str,
        worker_agent_id: str,
        parent_task_id: str,
        goal: str,
        requested_capabilities: list[AgentCapability],
        ttl_hours: int = 2,
        input_data: dict[str, Any] | None = None,
    ) -> DelegatedTask:
        """
        Delegate a sub-task from supervisor to worker agent and execute under active delegation.
        """
        expires_at = datetime.now(tz=UTC) + timedelta(hours=ttl_hours)

        delegation = await self.delegation_service.create_delegation(
            organization_id=organization_id,
            delegator_agent_id=supervisor_agent_id,
            delegate_agent_id=worker_agent_id,
            parent_task_id=parent_task_id,
            requested_capabilities=requested_capabilities,
            expires_at=expires_at,
        )

        return await self.executor.execute_delegated_task(
            organization_id=organization_id,
            delegation_id=delegation.delegation_id,
            goal=goal,
            input_data=input_data,
        )

    def aggregate_results(
        self,
        task_results: list[dict[str, Any]],
        title: str = "Aggregated Supervisor Report",
    ) -> dict[str, Any]:
        """
        Aggregate worker sub-task results into a consolidated report payload.
        Note: State mutations must still go through CommandBus.
        """
        aggregated: dict[str, Any] = {
            "title": title,
            "total_subtasks": len(task_results),
            "subtask_outputs": task_results,
            "timestamp": datetime.now(tz=UTC).isoformat(),
        }
        return aggregated

    async def cancel_delegated_task(
        self,
        organization_id: str,
        delegation_id: str,
    ) -> Delegation:
        """Cancel delegation and stop downstream execution."""
        return await self.delegation_service.cancel_delegation(organization_id, delegation_id)

    async def revoke_delegation(
        self,
        organization_id: str,
        delegation_id: str,
        reason: str,
    ) -> Delegation:
        """Revoke active delegation."""
        return await self.delegation_service.revoke_delegation(organization_id, delegation_id, reason=reason)
