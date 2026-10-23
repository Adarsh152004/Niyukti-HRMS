"""Tests — Tenant and Agent Memory Security Boundaries."""

import pytest

from backend.agents.domain.exceptions import AgentSecurityError
from backend.agents.memory.application.memory_service import MemoryService


@pytest.mark.asyncio
async def test_cross_tenant_memory_access_denied():
    mem_service = MemoryService()
    mem_a = await mem_service.record_memory(
        organization_id="org-tenant-a",
        agent_id="agent-a",
        content="Secret data tenant A",
    )

    # Attempting to fetch Tenant A memory under Tenant B organization ID returns None
    result = await mem_service.get_memory_by_id("org-tenant-b", mem_a.memory_id)
    assert result is None


@pytest.mark.asyncio
async def test_cross_agent_memory_access_denied():
    mem_service = MemoryService()
    mem_a = await mem_service.record_memory(
        organization_id="org-acme",
        agent_id="agent-a",
        content="Agent A memory",
    )

    # Agent B requesting Agent A's memory throws AgentSecurityError
    with pytest.raises(AgentSecurityError, match="Cross-agent memory access denied"):
        await mem_service.get_memory_by_id(
            organization_id="org-acme",
            memory_id=mem_a.memory_id,
            requesting_agent_id="agent-b",
        )
