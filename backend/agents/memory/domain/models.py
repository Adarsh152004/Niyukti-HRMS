"""
Agent Memory — Domain entity for AgentMemory.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.agents.memory.domain.enums import MemoryType


class AgentMemory(BaseModel):
    """
    Tenant-isolated, agent-scoped memory record.
    """

    memory_id: str = Field(default_factory=lambda: f"mem-{uuid.uuid4()}")
    organization_id: str = Field(description="Tenant ID boundary")
    agent_id: str = Field(description="Target Agent ID")
    task_id: str | None = Field(default=None)
    memory_type: MemoryType = Field(default=MemoryType.OBSERVATION)
    content: str = Field(description="Structured summary content (no secrets)")
    importance: float = Field(default=1.0, description="Importance score 0.0 to 1.0")
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    expires_at: datetime | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)
