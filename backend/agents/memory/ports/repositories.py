"""
Agent Memory Ports — Abstract Repository Interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from backend.agents.memory.domain.models import AgentMemory


class AgentMemoryRepositoryPort(ABC):
    @abstractmethod
    async def save(self, memory: AgentMemory) -> AgentMemory:
        pass

    @abstractmethod
    async def get_by_id(self, organization_id: str, memory_id: str) -> AgentMemory | None:
        pass

    @abstractmethod
    async def list_for_agent(self, organization_id: str, agent_id: str, limit: int = 10) -> Sequence[AgentMemory]:
        pass

    @abstractmethod
    async def list_for_task(self, organization_id: str, task_id: str) -> Sequence[AgentMemory]:
        pass
