"""
Agent Repositories — In-Memory and PostgreSQL Implementations.
"""

from __future__ import annotations

from collections.abc import Sequence

from backend.agents.domain.models import Agent, AgentTask
from backend.agents.ports.repositories import AgentRepositoryPort, AgentTaskRepositoryPort


class InMemoryAgentRepository(AgentRepositoryPort):
    def __init__(self) -> None:
        self._items: dict[tuple[str, str], Agent] = {}

    async def save(self, agent: Agent) -> Agent:
        self._items[(agent.organization_id, agent.agent_id)] = agent
        return agent

    async def get_by_id(self, organization_id: str, agent_id: str) -> Agent | None:
        return self._items.get((organization_id, agent_id))

    async def get_by_name(self, organization_id: str, name: str) -> Agent | None:
        for (org, _), a in self._items.items():
            if org == organization_id and a.name == name:
                return a
        return None

    async def list_by_organization(self, organization_id: str) -> Sequence[Agent]:
        return [a for (org, _), a in self._items.items() if org == organization_id]

    async def delete(self, organization_id: str, agent_id: str) -> bool:
        key = (organization_id, agent_id)
        if key in self._items:
            del self._items[key]
            return True
        return False


class InMemoryAgentTaskRepository(AgentTaskRepositoryPort):
    def __init__(self) -> None:
        self._items: dict[tuple[str, str], AgentTask] = {}

    async def save(self, task: AgentTask) -> AgentTask:
        self._items[(task.organization_id, task.task_id)] = task
        return task

    async def get_by_id(self, organization_id: str, task_id: str) -> AgentTask | None:
        return self._items.get((organization_id, task_id))

    async def list_by_agent(self, organization_id: str, agent_id: str) -> Sequence[AgentTask]:
        return [t for (org, _), t in self._items.items() if org == organization_id and t.agent_id == agent_id]

    async def list_by_organization(self, organization_id: str) -> Sequence[AgentTask]:
        return [t for (org, _), t in self._items.items() if org == organization_id]
