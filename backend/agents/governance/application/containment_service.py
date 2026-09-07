"""
Containment Service — Policy-driven emergency containment control plane for AI Agents.
Executes deterministic containment actions via AgentLifecycleManager.
Direct database status mutation is strictly prohibited.
AI Agents CANNOT contain agents or resolve their own containments.
"""

from __future__ import annotations

import logging

from backend.agents.application.agent_lifecycle import AgentLifecycleManager
from backend.agents.application.agent_service import AgentService
from backend.agents.governance.domain.enums import ContainmentActionType
from backend.agents.governance.domain.exceptions import ContainmentError, GovernanceAccessDeniedError
from backend.agents.governance.domain.models import ContainmentAction
from backend.agents.governance.infrastructure.database.repositories import InMemoryGovernanceRepository
from backend.agents.governance.ports.repositories import GovernanceRepositoryPort
from backend.hrms.domain.actor import Actor, ActorType
from backend.runtime.events import Event, EventBus

logger = logging.getLogger(__name__)


class ContainmentService:
    """
    Application Service executing safety containment actions on AI Agents.
    """

    def __init__(
        self,
        agent_service: AgentService | None = None,
        repository: GovernanceRepositoryPort | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.agent_service = agent_service or AgentService()
        self.repository = repository or InMemoryGovernanceRepository()
        self.event_bus = event_bus or EventBus.get_instance()

    async def execute_containment(
        self,
        organization_id: str,
        agent_id: str,
        action_type: ContainmentActionType,
        reason: str,
        triggered_by: Actor,
    ) -> ContainmentAction:
        """
        Execute a deterministic containment action on an agent using AgentLifecycleManager.
        """
        if triggered_by.actor_type == ActorType.AI_AGENT:
            raise GovernanceAccessDeniedError("AI Agents are strictly prohibited from executing containment actions.")

        if triggered_by.organization_id != organization_id:
            raise GovernanceAccessDeniedError("Actor organization mismatch.")

        agent = await self.agent_service.get_agent(organization_id, agent_id)
        if not agent:
            raise ContainmentError(f"Agent '{agent_id}' not found in organization '{organization_id}'.")

        previous_status = agent.status.value

        # Execute transition via AgentLifecycleManager
        if action_type == ContainmentActionType.PAUSE:
            AgentLifecycleManager.pause(agent)
        elif action_type == ContainmentActionType.SUSPEND:
            AgentLifecycleManager.suspend(agent)
        elif action_type == ContainmentActionType.DISABLE:
            AgentLifecycleManager.disable(agent)
        elif action_type == ContainmentActionType.TERMINATE:
            AgentLifecycleManager.terminate(agent)

        await self.agent_service.registry.save_agent(agent)

        record = ContainmentAction(
            organization_id=organization_id,
            agent_id=agent_id,
            action=action_type,
            reason=reason,
            triggered_by=triggered_by.actor_id,
            previous_status=previous_status,
            resulting_status=agent.status.value,
        )

        saved = await self.repository.save_containment_action(record)
        logger.warning(f"Containment [{action_type.value}] executed on agent '{agent_id}' by '{triggered_by.actor_id}': {reason}")

        await self.event_bus.publish(
            Event(
                event_type="hrms.agent.containment_triggered",
                source="containment_service",
                payload={
                    "containment_id": saved.containment_id,
                    "agent_id": agent_id,
                    "organization_id": organization_id,
                    "action": action_type.value,
                    "reason": reason,
                    "previous_status": previous_status,
                    "resulting_status": agent.status.value,
                },
            )
        )

        return saved

    async def resolve_containment(
        self,
        organization_id: str,
        agent_id: str,
        containment_id: str,
        resolver_actor: Actor,
        reason: str = "Admin resolved containment",
    ) -> ContainmentAction:
        """
        Resolve an active containment and re-activate agent.
        SECURITY INVARIANT: Approver MUST be HUMAN. AI Agents CANNOT resolve containments!
        """
        if resolver_actor.actor_type == ActorType.AI_AGENT:
            raise GovernanceAccessDeniedError("AI Agents are strictly prohibited from resolving containment actions.")

        if resolver_actor.organization_id != organization_id:
            raise GovernanceAccessDeniedError("Actor organization mismatch.")

        agent = await self.agent_service.get_agent(organization_id, agent_id)
        if not agent:
            raise ContainmentError(f"Agent '{agent_id}' not found in organization '{organization_id}'.")

        # Reactivate agent via AgentLifecycleManager
        AgentLifecycleManager.activate(agent)
        await self.agent_service.registry.save_agent(agent)

        record = ContainmentAction(
            organization_id=organization_id,
            agent_id=agent_id,
            action=ContainmentActionType.WARN,  # Resolution marker
            reason=f"RESOLVED: {reason}",
            triggered_by=resolver_actor.actor_id,
            previous_status="CONTAINED",
            resulting_status=agent.status.value,
        )

        return await self.repository.save_containment_action(record)
