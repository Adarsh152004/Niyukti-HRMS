"""
Delegation Executor — Executes sub-tasks assigned to worker agents under active delegation grants.
Enforces capability scoping, tenant isolation, and routing via ToolExecutionGateway -> AgentCommandGateway -> CommandBus.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from backend.agents.application.agent_service import AgentService
from backend.agents.application.execution_context import AgentExecutionContextFactory
from backend.agents.application.task_service import AgentTaskService
from backend.agents.delegation.application.delegation_service import DelegationService
from backend.agents.delegation.domain.enums import DelegationStatus
from backend.agents.delegation.domain.exceptions import DelegationAccessDeniedError, DelegationExpiredError
from backend.agents.delegation.domain.models import DelegatedTask
from backend.agents.domain.enums import AgentStatus
from backend.agents.domain.models import Agent
from backend.agents.reasoning.application.reasoning_engine import ReasoningEngine
from backend.agents.tools.application.tool_gateway import ToolExecutionGateway
from backend.hrms.domain.actor import Actor, ActorType

logger = logging.getLogger(__name__)


class DelegationExecutor:
    """
    Executes delegated tasks using worker agents scoped strictly to delegated capabilities.
    """

    def __init__(
        self,
        delegation_service: DelegationService | None = None,
        agent_service: AgentService | None = None,
        task_service: AgentTaskService | None = None,
        tool_gateway: ToolExecutionGateway | None = None,
        reasoning_engine: ReasoningEngine | None = None,
    ) -> None:
        self.delegation_service = delegation_service or DelegationService()
        self.agent_service = agent_service or AgentService()
        self.task_service = task_service or AgentTaskService()
        self.tool_gateway = tool_gateway or ToolExecutionGateway()
        self.reasoning_engine = reasoning_engine or ReasoningEngine(
            tool_gateway=self.tool_gateway,
            agent_service=self.agent_service,
            task_service=self.task_service,
        )

    async def execute_delegated_task(
        self,
        organization_id: str,
        delegation_id: str,
        goal: str,
        input_data: dict[str, Any] | None = None,
    ) -> DelegatedTask:
        """
        Execute sub-task assigned to worker agent under active delegation.
        """
        delegation = await self.delegation_service.get_delegation(organization_id, delegation_id)
        if not delegation:
            raise ValueError(f"Delegation '{delegation_id}' not found.")

        if not delegation.is_active():
            if delegation.status == DelegationStatus.EXPIRED or datetime.now(tz=UTC) >= delegation.expires_at:
                raise DelegationExpiredError(f"Delegation '{delegation_id}' is EXPIRED.")
            raise DelegationAccessDeniedError(f"Delegation '{delegation_id}' is not ACTIVE (status: {delegation.status}).")

        # Verify worker and delegator status
        delegator = await self.agent_service.get_agent(organization_id, delegation.delegator_agent_id)
        if not delegator or delegator.status != AgentStatus.ACTIVE:
            raise DelegationAccessDeniedError(f"Delegator agent '{delegation.delegator_agent_id}' is not ACTIVE.")

        delegate_raw = await self.agent_service.get_agent(organization_id, delegation.delegate_agent_id)
        if not delegate_raw or delegate_raw.status != AgentStatus.ACTIVE:
            raise DelegationAccessDeniedError(f"Delegate worker agent '{delegation.delegate_agent_id}' is not ACTIVE.")

        # Construct worker agent scoped strictly to delegated capabilities
        scoped_worker = Agent(
            agent_id=delegate_raw.agent_id,
            organization_id=organization_id,
            name=delegate_raw.name,
            display_name=delegate_raw.display_name,
            actor_id=delegate_raw.actor_id,
            status=AgentStatus.ACTIVE,
            capabilities=delegation.capabilities,  # Scoped capability subset!
            metadata=delegate_raw.metadata,
        )

        # Create delegated task record
        delegated_task = DelegatedTask(
            delegation_id=delegation.delegation_id,
            organization_id=organization_id,
            delegator_agent_id=delegation.delegator_agent_id,
            delegate_agent_id=delegation.delegate_agent_id,
            goal=goal,
            status="RUNNING",
        )
        await self.delegation_service.repository.save_delegated_task(delegated_task)

        # Create AgentTask in task service
        agent_task = await self.task_service.create_task(
            organization_id=organization_id,
            agent_id=scoped_worker.agent_id,
            goal=goal,
            input_payload=input_data or {},
            parent_task_id=delegation.parent_task_id,
        )
        await self.task_service.start_task(organization_id, agent_task.task_id)

        # Build execution context for worker agent
        worker_actor = Actor(
            actor_id=scoped_worker.actor_id,
            actor_type=ActorType.AI_AGENT,
            organization_id=organization_id,
            permissions=set(),  # Capability enforcement handled via scoped capabilities & CommandBus
        )
        ctx = AgentExecutionContextFactory.create_context(scoped_worker, agent_task, actor=worker_actor)

        # Execute reasoning loop for worker agent
        run = await self.reasoning_engine.run_task_reasoning(
            agent=scoped_worker,
            task=agent_task,
            context=ctx,
            actor=worker_actor,
        )

        # Extract worker task output
        if run.status in ["COMPLETED", "PAUSED", "IN_PROGRESS"]:
            delegated_task.status = "COMPLETED"
            delegated_task.result = agent_task.output or {"status": "SUCCESS"}
            delegated_task.completed_at = datetime.now(tz=UTC)
            await self.task_service.complete_task(organization_id, agent_task.task_id, output=delegated_task.result)

            # Complete delegation if single task scope
            delegation.delegated_task_id = agent_task.task_id
            delegation.transition_to(DelegationStatus.COMPLETED)
            await self.delegation_service.repository.save_delegation(delegation)
        else:
            delegated_task.status = "FAILED"
            delegated_task.failure_reason = run.metadata.get("error", "Delegated worker task failed.")
            await self.task_service.fail_task(organization_id, agent_task.task_id, reason=delegated_task.failure_reason)

            delegation.transition_to(DelegationStatus.FAILED)
            await self.delegation_service.repository.save_delegation(delegation)

        await self.delegation_service.repository.save_delegated_task(delegated_task)
        return delegated_task
