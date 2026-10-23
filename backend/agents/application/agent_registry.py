"""
Agent Registry — Tenant-Scoped AI Agent Registry and Capability Discovery.
"""

from __future__ import annotations

from collections.abc import Sequence

from backend.agents.domain.exceptions import AgentNotFoundError, AgentSecurityError
from backend.agents.domain.models import Agent
from backend.agents.infrastructure.database.repositories import InMemoryAgentRepository
from backend.agents.ports.repositories import AgentRepositoryPort


class AgentRegistry:
    """
    Registry for managing AI Agent identities, capabilities, and lookups.
    """

    def __init__(self, repository: AgentRepositoryPort | None = None) -> None:
        self.repository = repository or InMemoryAgentRepository()

    async def register_agent(self, agent: Agent) -> Agent:
        """Register a new AI Agent enforcing uniqueness within tenant."""
        existing = await self.repository.get_by_name(agent.organization_id, agent.name)
        if existing:
            raise AgentSecurityError(f"Agent with name '{agent.name}' already exists in tenant '{agent.organization_id}'.")
        return await self.repository.save(agent)

    async def get_agent(self, organization_id: str, agent_id: str) -> Agent:
        """Retrieve an agent by tenant and agent ID."""
        agent = await self.repository.get_by_id(organization_id, agent_id)
        if not agent:
            raise AgentNotFoundError(f"Agent '{agent_id}' not found in tenant '{organization_id}'.")
        return agent

    async def list_agents(self, organization_id: str) -> Sequence[Agent]:
        """List all agents for tenant."""
        return await self.repository.list_by_organization(organization_id)

    async def save_agent(self, agent: Agent) -> Agent:
        """Save updated agent entity."""
        return await self.repository.save(agent)

    async def delete_agent(self, organization_id: str, agent_id: str) -> bool:
        """Delete agent entity."""
        return await self.repository.delete(organization_id, agent_id)
