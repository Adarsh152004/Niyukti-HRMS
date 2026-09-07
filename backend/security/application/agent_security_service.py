"""
AI Agent Security Service — Agent Registration, Capability Scoping, and Independent Authentication.

Enforces:
- AI agents possess explicit capability grants (`capabilities`).
- AI agents authenticate independently as `ActorType.AI_AGENT`.
- AI agents CANNOT impersonate human JWTs or acquire ungranted admin roles.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime

from backend.hrms.domain.actor import Actor, ActorType
from backend.security.domain.enums import AgentStatus
from backend.security.domain.models import AgentIdentity


class AgentAuthenticationError(Exception):
    """Raised when agent authentication or capability checks fail."""

    pass


class AgentSecurityService:
    """
    Service managing AI Agent security identities and capabilities.
    """

    def __init__(self) -> None:
        self._agents_by_id: dict[str, AgentIdentity] = {}
        self._agents_by_actor: dict[str, AgentIdentity] = {}

    def register_agent(
        self,
        name: str,
        organization_id: str,
        capabilities: set[str] | list[str],
        description: str | None = None,
        handler_actor_id: str | None = None,
    ) -> AgentIdentity:
        """Register a new AI Agent identity with explicit capabilities."""
        now = datetime.now(tz=UTC)
        actor_id = f"agent-actor-{name.lower().replace(' ', '-')}"

        agent = AgentIdentity(
            actor_id=actor_id,
            organization_id=organization_id,
            name=name,
            description=description,
            status=AgentStatus.ACTIVE,
            capabilities=set(capabilities),
            handler_actor_id=handler_actor_id,
            created_at=now,
            updated_at=now,
        )
        self._agents_by_id[agent.agent_id] = agent
        self._agents_by_actor[agent.actor_id] = agent
        return agent

    def authenticate_agent(self, agent_id: str, organization_id: str) -> Actor:
        """
        Authenticate an AI Agent independently.
        Returns the mapped Actor object with ActorType.AI_AGENT.
        """
        agent = self._agents_by_id.get(agent_id)
        if not agent:
            raise AgentAuthenticationError(f"Agent '{agent_id}' not found.")

        if agent.organization_id != organization_id:
            raise AgentAuthenticationError("Tenant boundary violation during agent authentication.")

        if agent.status != AgentStatus.ACTIVE:
            raise AgentAuthenticationError(f"Agent '{agent.name}' authentication blocked: status is '{agent.status.value}'.")

        agent.updated_at = datetime.now(tz=UTC)
        return Actor(
            actor_id=agent.actor_id,
            actor_type=ActorType.AI_AGENT,
            organization_id=agent.organization_id,
            identity=f"agent:{agent.name}",
            roles={"AI_AGENT"},
            permissions=set(),  # Agents do not get raw human permissions automatically
            metadata={"agent_id": agent.agent_id, "capabilities": list(agent.capabilities)},
        )

    def suspend_agent(self, agent_id: str) -> AgentIdentity:
        """Suspend an AI agent, blocking its authentication."""
        agent = self._agents_by_id.get(agent_id)
        if not agent:
            raise ValueError(f"Agent '{agent_id}' not found.")
        agent.status = AgentStatus.SUSPENDED
        agent.updated_at = datetime.now(tz=UTC)
        return agent

    def revoke_agent(self, agent_id: str) -> AgentIdentity:
        """Revoke an AI agent permanently."""
        agent = self._agents_by_id.get(agent_id)
        if not agent:
            raise ValueError(f"Agent '{agent_id}' not found.")
        agent.status = AgentStatus.REVOKED
        agent.updated_at = datetime.now(tz=UTC)
        return agent

    def update_capabilities(self, agent_id: str, capabilities: set[str] | list[str]) -> AgentIdentity:
        """Update explicit capabilities assigned to an agent."""
        agent = self._agents_by_id.get(agent_id)
        if not agent:
            raise ValueError(f"Agent '{agent_id}' not found.")
        agent.capabilities = set(capabilities)
        agent.updated_at = datetime.now(tz=UTC)
        return agent

    def get_agent_by_id(self, agent_id: str) -> AgentIdentity | None:
        return self._agents_by_id.get(agent_id)

    def list_agents_for_organization(self, organization_id: str) -> Sequence[AgentIdentity]:
        return [a for a in self._agents_by_id.values() if a.organization_id == organization_id]
