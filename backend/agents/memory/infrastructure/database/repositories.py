"""
Agent Memory Repositories — In-Memory Implementation.
"""

from __future__ import annotations

from collections.abc import Sequence

from backend.agents.memory.domain.models import AgentMemory
from backend.agents.memory.ports.repositories import AgentMemoryRepositoryPort


class InMemoryAgentMemoryRepository(AgentMemoryRepositoryPort):
    def __init__(self) -> None:
        self._items: dict[tuple[str, str], AgentMemory] = {}

    async def save(self, memory: AgentMemory) -> AgentMemory:
        self._items[(memory.organization_id, memory.memory_id)] = memory
        return memory

    async def get_by_id(self, organization_id: str, memory_id: str) -> AgentMemory | None:
        return self._items.get((organization_id, memory_id))

    async def list_for_agent(self, organization_id: str, agent_id: str, limit: int = 10) -> Sequence[AgentMemory]:
        items = [m for (org, _), m in self._items.items() if org == organization_id and m.agent_id == agent_id]
        items.sort(key=lambda x: x.created_at, reverse=True)
        return items[:limit]

    async def list_for_task(self, organization_id: str, task_id: str) -> Sequence[AgentMemory]:
        return [m for (org, _), m in self._items.items() if org == organization_id and m.task_id == task_id]
