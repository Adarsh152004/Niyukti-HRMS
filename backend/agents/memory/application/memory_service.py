"""
Memory Service — Manages tenant-isolated and agent-scoped memory storage and retrieval.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from backend.agents.domain.exceptions import AgentSecurityError
from backend.agents.memory.domain.enums import MemoryType
from backend.agents.memory.domain.models import AgentMemory
from backend.agents.memory.infrastructure.database.repositories import InMemoryAgentMemoryRepository
from backend.agents.memory.ports.repositories import AgentMemoryRepositoryPort


class MemoryService:
    """
    Tenant-isolated and agent-scoped memory management service.
    """

    def __init__(self, repository: AgentMemoryRepositoryPort | None = None) -> None:
        self.repository = repository or InMemoryAgentMemoryRepository()

    async def record_memory(
        self,
        organization_id: str,
        agent_id: str,
        content: str,
        memory_type: MemoryType = MemoryType.OBSERVATION,
        task_id: str | None = None,
        importance: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> AgentMemory:
        """Create and store a memory record."""
        memory = AgentMemory(
            organization_id=organization_id,
            agent_id=agent_id,
            task_id=task_id,
            memory_type=memory_type,
            content=content,
            importance=importance,
            metadata=metadata or {},
        )
        return await self.repository.save(memory)

    async def get_memories_for_agent(self, organization_id: str, agent_id: str, limit: int = 10) -> Sequence[AgentMemory]:
        """Retrieve recent memories for agent strictly within tenant boundary."""
        return await self.repository.list_for_agent(organization_id, agent_id, limit=limit)

    async def get_memory_by_id(
        self, organization_id: str, memory_id: str, requesting_agent_id: str | None = None
    ) -> AgentMemory | None:
        """Retrieve a specific memory checking tenant isolation and agent ownership."""
        mem = await self.repository.get_by_id(organization_id, memory_id)
        if mem and requesting_agent_id and mem.agent_id != requesting_agent_id:
            raise AgentSecurityError("Cross-agent memory access denied.")
        return mem
