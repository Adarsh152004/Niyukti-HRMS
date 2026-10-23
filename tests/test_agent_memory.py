"""Tests — MemoryService CRUD, retrieval, and ContextBuilder bounded prompting."""

import pytest

from backend.agents.application.execution_context import AgentExecutionContextFactory
from backend.agents.domain.enums import AgentStatus
from backend.agents.domain.models import Agent, AgentCapability, AgentTask
from backend.agents.memory.application.context_builder import ContextBuilder
from backend.agents.memory.application.memory_service import MemoryService
from backend.agents.memory.domain.enums import MemoryType


@pytest.mark.asyncio
async def test_memory_service_record_and_retrieve():
    mem_service = MemoryService()
    mem = await mem_service.record_memory(
        organization_id="org-acme",
        agent_id="agent-1",
        content="Employee #101 was onboarded successfully.",
        memory_type=MemoryType.FACT,
    )

    assert mem.memory_id.startswith("mem-")
    memories = await mem_service.get_memories_for_agent("org-acme", "agent-1")
    assert len(memories) == 1
    assert memories[0].content == "Employee #101 was onboarded successfully."


@pytest.mark.asyncio
async def test_context_builder_bounded_context():
    mem_service = MemoryService()
    await mem_service.record_memory(
        organization_id="org-acme",
        agent_id="agent-1",
        content="Important memory 1",
    )

    cap_read = AgentCapability(
        capability_id="cap-1",
        name="Read Emp",
        resource="employee",
        actions=["read"],
    )

    agent = Agent(
        agent_id="agent-1",
        organization_id="org-acme",
        name="agent-1",
        display_name="Agent 1",
        actor_id="actor-1",
        status=AgentStatus.ACTIVE,
        capabilities=[cap_read],
    )

    task = AgentTask(organization_id="org-acme", agent_id=agent.agent_id, goal="Test context")
    ctx = AgentExecutionContextFactory.create_context(agent, task)

    builder = ContextBuilder(memory_service=mem_service)
    bounded_ctx = await builder.build_context(agent, task, ctx)

    assert bounded_ctx.agent_id == agent.agent_id
    assert bounded_ctx.task_goal == "Test context"
    assert len(bounded_ctx.memories) == 1
    assert bounded_ctx.memories[0] == "Important memory 1"
