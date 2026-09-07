"""
Agent Command Gateway — THE ONLY ALLOWED INTERFACE for AI Agents to request state-changing operations.

CRITICAL SECURITY INVARIANTS:
1. Agents CANNOT access repositories or database directly.
2. Every state mutation MUST flow through CommandBus:
   Agent -> AgentCommandGateway -> Command -> CommandBus -> Policy -> Auth -> Risk -> HITL -> ActionExecutor -> UoW -> Outbox
3. Validates agent active status, tenant isolation, and capability declarations before constructing and dispatching Command.
"""

from __future__ import annotations

from typing import Any

from backend.agents.domain.enums import AgentStatus
from backend.agents.domain.exceptions import AgentCapabilityError, AgentSecurityError
from backend.agents.domain.models import Agent, AgentExecutionContext
from backend.commands.application.bus import CommandBus
from backend.commands.domain.enums import CommandChannel
from backend.commands.domain.models import Command, CommandResult
from backend.hrms.domain.actor import Actor, ActorType


class AgentCommandGateway:
    """
    Gatekeeper interface enforcing security boundaries when AI Agents propose actions.
    """

    def __init__(self, command_bus: CommandBus | None = None) -> None:
        self.command_bus = command_bus or CommandBus()

    async def request_action(
        self,
        agent: Agent,
        context: AgentExecutionContext,
        resource: str,
        action: str,
        command_type: str,
        payload: dict[str, Any],
        actor: Actor | None = None,
    ) -> CommandResult:
        """
        Validate Agent status, tenant isolation, and capability alignment,
        then dispatch Command via Node 5 CommandBus pipeline.
        """
        # 1. Validate Agent status
        if agent.status != AgentStatus.ACTIVE:
            raise AgentSecurityError(f"Agent '{agent.agent_id}' cannot execute action in status '{agent.status.value}'.")

        # 2. Validate Tenant Isolation
        if agent.organization_id != context.organization_id:
            raise AgentSecurityError(
                f"Cross-tenant access attempt: Agent org '{agent.organization_id}' != Context org '{context.organization_id}'."
            )

        # 3. Validate Capability Declaration
        if not agent.has_capability(resource=resource, action=action):
            raise AgentCapabilityError(f"Agent '{agent.name}' lacks required capability '{resource}:{action}'.")

        # Construct Agent Actor for CommandBus
        agent_actor = actor or Actor(
            actor_id=agent.actor_id,
            actor_type=ActorType.AI_AGENT,
            organization_id=agent.organization_id,
            identity=f"ai_agent:{agent.name}",
        )

        # 4. Construct Command
        command = Command(
            command_type=command_type,
            actor_id=agent_actor.actor_id,
            organization_id=agent.organization_id,
            channel=CommandChannel.AGENT,
            payload=payload,
            correlation_id=context.correlation_id,
        )

        # 5. Build Trusted CommandContext
        cmd_context = self.command_bus.build_context(
            actor=agent_actor,
            channel=CommandChannel.AGENT,
        )

        # 6. Dispatch through Node 5 CommandBus pipeline
        return await self.command_bus.dispatch(command, cmd_context)
