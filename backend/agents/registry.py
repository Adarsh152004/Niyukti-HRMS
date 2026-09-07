"""
Agent Framework — Agent Registry.

Central registry for all active HRMS agent instances.
Agents are registered by their role and unique ID.
"""

from __future__ import annotations

from backend.agents.base import AgentStatus, BaseAgent


class AgentNotFoundError(Exception):
    """Raised when an agent is not found in the registry."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Agent not found: {identifier!r}")


class AgentRegistry:
    """
    Registry for active HRMS agent instances.

    Provides registration, resolution by ID or role, status querying,
    and lifecycle state management across all agents.
    """

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}  # agent_id → agent

    def register(self, agent: BaseAgent) -> None:
        """Register an agent. Raises if already registered."""
        if agent.agent_id in self._agents:
            raise ValueError(f"Agent {agent.agent_id!r} is already registered.")
        self._agents[agent.agent_id] = agent

    def unregister(self, agent_id: str) -> None:
        """Remove an agent from the registry. No-op if not found."""
        self._agents.pop(agent_id, None)

    def get_by_id(self, agent_id: str) -> BaseAgent:
        """Resolve an agent by its unique ID. Raises AgentNotFoundError if missing."""
        if agent_id not in self._agents:
            raise AgentNotFoundError(agent_id)
        return self._agents[agent_id]

    def get_by_role(self, role: str) -> list[BaseAgent]:
        """Return all registered agents with the given role."""
        return [a for a in self._agents.values() if a.role == role]

    def list_all(self) -> list[BaseAgent]:
        """Return all registered agents."""
        return list(self._agents.values())

    def list_active(self) -> list[BaseAgent]:
        """Return all agents currently in ACTIVE status."""
        return [a for a in self._agents.values() if a.status == AgentStatus.ACTIVE]

    def count(self) -> int:
        """Return total registered agent count."""
        return len(self._agents)

    def summary(self) -> list[dict[str, str]]:
        """Return a non-PII summary of all registered agents."""
        return [
            {
                "agent_id": a.agent_id,
                "role": a.role,
                "status": a.status.value,
            }
            for a in self._agents.values()
        ]

    def __repr__(self) -> str:
        return f"AgentRegistry(count={self.count()})"
