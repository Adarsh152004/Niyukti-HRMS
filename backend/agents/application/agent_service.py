"""
Agent Service — High-level application service orchestrating Agent creation, lifecycle, and event emission.
"""

from __future__ import annotations

from typing import Any

from backend.agents.application.agent_lifecycle import AgentLifecycleManager
from backend.agents.application.agent_registry import AgentRegistry
from backend.agents.domain.enums import AgentStatus, AgentType
from backend.agents.domain.events import (
    AgentActivated,
    AgentDisabled,
    AgentPaused,
    AgentRegistered,
    AgentSuspended,
    AgentTerminated,
)
from backend.agents.domain.models import Agent, AgentCapability
from backend.hrms.domain.actor import Actor, ActorType
from backend.runtime.events import EventBus


class AgentService:
    """
    Application Service managing AI Agent lifecycles and domain event emissions.
    """

    _instance: AgentService | None = None

    def __init__(
        self,
        registry: AgentRegistry | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.registry = registry or AgentRegistry()
        self.event_bus = event_bus or EventBus.get_instance()

    @classmethod
    def get_instance(cls) -> AgentService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_agent(self, agent: Agent) -> None:
        """Synchronously record agent in internal registry if present."""
        if hasattr(self.registry, "save_agent_sync"):
            self.registry.save_agent_sync(agent)

    async def create_agent(
        self,
        organization_id: str,
        name: str,
        display_name: str,
        description: str = "",
        agent_type: AgentType = AgentType.CUSTOM_AGENT,
        capabilities: list[AgentCapability] | None = None,
        actor_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Agent:
        """Create and register a new AI Agent."""
        mapped_actor_id = actor_id or f"actor-{name}"
        agent = Agent(
            organization_id=organization_id,
            name=name,
            display_name=display_name,
            description=description,
            agent_type=agent_type,
            status=AgentStatus.CREATED,
            actor_id=mapped_actor_id,
            capabilities=capabilities or [],
            metadata=metadata or {},
        )

        registered = await self.registry.register_agent(agent)

        actor_snapshot = Actor(
            actor_id=mapped_actor_id,
            actor_type=ActorType.AI_AGENT,
            organization_id=organization_id,
            identity=f"ai_agent:{name}",
        ).model_dump()

        await self.event_bus.publish(
            AgentRegistered(
                organization_id=organization_id,
                aggregate_id=registered.agent_id,
                actor=actor_snapshot,
                metadata={"name": name, "agent_type": agent_type.value},
            )
        )

        return registered

    async def activate_agent(self, organization_id: str, agent_id: str) -> Agent:
        agent = await self.registry.get_agent(organization_id, agent_id)
        AgentLifecycleManager.activate(agent)
        saved = await self.registry.save_agent(agent)
        await self.event_bus.publish(
            AgentActivated(
                organization_id=organization_id,
                aggregate_id=agent.agent_id,
                actor={"actor_id": agent.actor_id, "actor_type": "AI_AGENT"},
                metadata={"status": agent.status.value},
            )
        )
        return saved

    async def pause_agent(self, organization_id: str, agent_id: str) -> Agent:
        agent = await self.registry.get_agent(organization_id, agent_id)
        AgentLifecycleManager.pause(agent)
        saved = await self.registry.save_agent(agent)
        await self.event_bus.publish(
            AgentPaused(
                organization_id=organization_id,
                aggregate_id=agent.agent_id,
                actor={"actor_id": agent.actor_id, "actor_type": "AI_AGENT"},
                metadata={"status": agent.status.value},
            )
        )
        return saved

    async def suspend_agent(self, organization_id: str, agent_id: str) -> Agent:
        agent = await self.registry.get_agent(organization_id, agent_id)
        AgentLifecycleManager.suspend(agent)
        saved = await self.registry.save_agent(agent)
        await self.event_bus.publish(
            AgentSuspended(
                organization_id=organization_id,
                aggregate_id=agent.agent_id,
                actor={"actor_id": agent.actor_id, "actor_type": "AI_AGENT"},
                metadata={"status": agent.status.value},
            )
        )
        return saved

    async def disable_agent(self, organization_id: str, agent_id: str) -> Agent:
        agent = await self.registry.get_agent(organization_id, agent_id)
        AgentLifecycleManager.disable(agent)
        saved = await self.registry.save_agent(agent)
        await self.event_bus.publish(
            AgentDisabled(
                organization_id=organization_id,
                aggregate_id=agent.agent_id,
                actor={"actor_id": agent.actor_id, "actor_type": "AI_AGENT"},
                metadata={"status": agent.status.value},
            )
        )
        return saved

    async def terminate_agent(self, organization_id: str, agent_id: str) -> Agent:
        agent = await self.registry.get_agent(organization_id, agent_id)
        AgentLifecycleManager.terminate(agent)
        saved = await self.registry.save_agent(agent)
        await self.event_bus.publish(
            AgentTerminated(
                organization_id=organization_id,
                aggregate_id=agent.agent_id,
                actor={"actor_id": agent.actor_id, "actor_type": "AI_AGENT"},
                metadata={"status": agent.status.value},
            )
        )
        return saved

    async def get_agent(self, organization_id: str, agent_id: str) -> Agent | None:
        """Retrieve agent by ID via registry."""
        return await self.registry.get_agent(organization_id, agent_id)

    async def list_agents(self, organization_id: str) -> list[Agent]:
        """List agents via registry."""
        return list(await self.registry.list_agents(organization_id))
