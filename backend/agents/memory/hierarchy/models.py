"""
Hierarchical Memory Domain Models — Structured memory records partitioned across tiers.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.agents.memory.domain.enums import MemoryType
from backend.agents.memory.hierarchy.enums import MemoryTier
from backend.knowledge.domain.enums import KnowledgeClassification


class HierarchicalMemoryRecord(BaseModel):
    """Immutable structured memory unit strictly bounded by tier and ownership."""

    memory_id: str = Field(default_factory=lambda: f"hmem-{uuid.uuid4()}")
    organization_id: str = Field(description="Tenant boundary")
    tier: MemoryTier = Field(default=MemoryTier.AGENT)
    memory_type: MemoryType = Field(default=MemoryType.OBSERVATION)
    classification: KnowledgeClassification = Field(default=KnowledgeClassification.INTERNAL)

    # Ownership Scopes
    agent_id: str | None = None  # Populated for AGENT tier
    team_id: str | None = None  # Populated for TEAM tier (e.g. "squad-recruitment")
    employee_id: str | None = None  # Populated for EMPLOYEE tier

    content: str = Field(description="Structured validated fact/result (no secrets or raw CoT)")
    importance_score: float = Field(default=1.0, ge=0.0, le=1.0)
    source_reference: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    expires_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
