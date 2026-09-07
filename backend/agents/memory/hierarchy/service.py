"""
Hierarchical Memory Service — Enforces strict partition isolation and access controls.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from backend.agents.memory.domain.enums import MemoryType
from backend.agents.memory.hierarchy.enums import MemoryTier
from backend.agents.memory.hierarchy.models import HierarchicalMemoryRecord
from backend.knowledge.domain.enums import KnowledgeClassification

logger = logging.getLogger(__name__)


class MemoryAccessDeniedError(Exception):
    """Raised when an actor or agent attempts unauthorized cross-tier or cross-tenant memory access."""

    pass


class HierarchicalMemoryService:
    """Service managing Agent, Team, Organization, and Employee memory partitions."""

    _instance: HierarchicalMemoryService | None = None

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._records: dict[str, HierarchicalMemoryRecord] = {}

    @classmethod
    def get_instance(cls) -> HierarchicalMemoryService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def write_memory(
        self,
        organization_id: str,
        tier: MemoryTier,
        content: str,
        memory_type: MemoryType = MemoryType.OBSERVATION,
        classification: KnowledgeClassification = KnowledgeClassification.INTERNAL,
        agent_id: str | None = None,
        team_id: str | None = None,
        employee_id: str | None = None,
        importance_score: float = 1.0,
        source_reference: str | None = None,
        expires_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> HierarchicalMemoryRecord:
        """
        Write a structured memory record.
        Enforces required owner identifiers per tier:
        - AGENT requires agent_id
        - TEAM requires team_id
        - EMPLOYEE requires employee_id
        """
        if tier == MemoryTier.AGENT and not agent_id:
            raise ValueError("AGENT tier memory requires a valid agent_id.")
        if tier == MemoryTier.TEAM and not team_id:
            raise ValueError("TEAM tier memory requires a valid team_id.")
        if tier == MemoryTier.EMPLOYEE and not employee_id:
            raise ValueError("EMPLOYEE tier memory requires a valid employee_id.")

        record = HierarchicalMemoryRecord(
            organization_id=organization_id,
            tier=tier,
            memory_type=memory_type,
            classification=classification,
            agent_id=agent_id,
            team_id=team_id,
            employee_id=employee_id,
            content=content,
            importance_score=importance_score,
            source_reference=source_reference,
            expires_at=expires_at,
            metadata=metadata or {},
        )

        async with self._lock:
            self._records[record.memory_id] = record
            logger.info(f"Recorded [{tier.value}] memory [{record.memory_id}] for org [{organization_id}]")
            return record

    async def read_memories(
        self,
        organization_id: str,
        tier: MemoryTier,
        requesting_actor_id: str,
        requesting_agent_id: str | None = None,
        agent_teams: Sequence[str] | None = None,
        employee_id: str | None = None,
    ) -> Sequence[HierarchicalMemoryRecord]:
        """
        Retrieve memory records strictly bounded by tier authorization rules:
        - AGENT: only requesting_agent_id can read its own agent memory.
        - TEAM: only agents belonging to team_id can read team memory.
        - ORGANIZATION: readable across the tenant.
        - EMPLOYEE: readable only for requesting employee or authorized HR/Admin.
        """
        now = datetime.now(tz=UTC)

        async with self._lock:
            results: list[HierarchicalMemoryRecord] = []

            for r in self._records.values():
                # 1. Strict Tenant Isolation
                if r.organization_id != organization_id:
                    continue

                # 2. Expiration filter
                if r.expires_at and r.expires_at < now:
                    continue

                # 3. Tier Filter & Access Check
                if r.tier != tier:
                    continue

                if tier == MemoryTier.AGENT:
                    if r.agent_id == requesting_agent_id:
                        results.append(r)

                elif tier == MemoryTier.TEAM:
                    if agent_teams and r.team_id in agent_teams:
                        results.append(r)

                elif tier == MemoryTier.ORGANIZATION:
                    results.append(r)

                elif tier == MemoryTier.EMPLOYEE:
                    target_id = employee_id or requesting_actor_id
                    if r.employee_id == target_id and requesting_actor_id == target_id:
                        results.append(r)

            return results

    async def clear(self) -> None:
        """Clear memory for testing."""
        async with self._lock:
            self._records.clear()
