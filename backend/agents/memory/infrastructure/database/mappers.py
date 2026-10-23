"""
Agent Memory Mappers — Bi-directional Domain ↕ Database Mappers.
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.agents.memory.domain.enums import MemoryType
from backend.agents.memory.domain.models import AgentMemory
from backend.agents.memory.infrastructure.database.models import AgentMemoryModel


class AgentMemoryMapper:
    @staticmethod
    def to_domain(model: AgentMemoryModel) -> AgentMemory:
        now = datetime.now(tz=UTC)
        return AgentMemory(
            memory_id=model.id,
            organization_id=model.organization_id,
            agent_id=model.agent_id,
            task_id=model.task_id,
            memory_type=MemoryType(model.memory_type),
            content=model.content,
            importance=model.importance,
            created_at=model.created_at or now,
            expires_at=model.expires_at,
            metadata=model.metadata_json or {},
        )

    @staticmethod
    def to_model(domain: AgentMemory) -> AgentMemoryModel:
        return AgentMemoryModel(
            id=domain.memory_id,
            organization_id=domain.organization_id,
            agent_id=domain.agent_id,
            task_id=domain.task_id,
            memory_type=domain.memory_type.value,
            content=domain.content,
            importance=domain.importance,
            created_at=domain.created_at,
            expires_at=domain.expires_at,
            metadata_json=domain.metadata,
        )
