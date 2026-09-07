"""
Context Builder — Assembles bounded prompt context for LLM reasoning engine.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel

from backend.agents.domain.models import Agent, AgentExecutionContext, AgentTask
from backend.agents.memory.application.memory_service import MemoryService
from backend.agents.tools.application.tool_discovery import ToolDiscovery
from backend.agents.tools.domain.models import ToolDefinition, ToolExecutionResult


class BoundedContext(BaseModel):
    """
    Bounded context payload passed to LLM reasoning provider.
    """

    agent_id: str
    agent_name: str
    agent_type: str
    organization_id: str
    task_id: str
    task_goal: str
    task_input: dict[str, Any]
    capabilities: list[str]
    allowed_tools: list[dict[str, Any]]
    memories: list[str]
    tool_results: list[dict[str, Any]]
    step_number: int


class ContextBuilder:
    """
    Constructs bounded LLM contexts respecting token/character limits.
    """

    def __init__(
        self,
        memory_service: MemoryService | None = None,
        tool_discovery: ToolDiscovery | None = None,
        max_memory_items: int = 5,
        max_context_chars: int = 4000,
    ) -> None:
        self.memory_service = memory_service or MemoryService()
        self.tool_discovery = tool_discovery or ToolDiscovery()
        self.max_memory_items = max_memory_items
        self.max_context_chars = max_context_chars

    async def build_context(
        self,
        agent: Agent,
        task: AgentTask,
        context: AgentExecutionContext,
        tool_results: list[ToolExecutionResult] | None = None,
        step_number: int = 1,
    ) -> BoundedContext:
        """
        Assemble bounded context combining execution context, task inputs, memories, and tools.
        """
        # 1. Discover allowed tools for agent
        tools: Sequence[ToolDefinition] = self.tool_discovery.discover_tools(agent, context)
        tool_schemas = [
            {
                "tool_id": t.tool_id,
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema,
                "requires_hitl": t.requires_hitl,
                "risk_level": t.risk_level,
            }
            for t in tools
        ]

        # 2. Retrieve recent memories
        memories_objs = await self.memory_service.get_memories_for_agent(
            organization_id=context.organization_id,
            agent_id=agent.agent_id,
            limit=self.max_memory_items,
        )
        memory_texts = [m.content for m in memories_objs]

        # 3. Format tool execution history
        formatted_results = [
            {
                "proposal_id": r.proposal_id,
                "tool_id": r.tool_id,
                "status": r.status,
                "data": r.data,
                "error": r.error,
            }
            for r in (tool_results or [])
        ]

        return BoundedContext(
            agent_id=agent.agent_id,
            agent_name=agent.display_name,
            agent_type=agent.agent_type.value,
            organization_id=context.organization_id,
            task_id=task.task_id,
            task_goal=task.goal,
            task_input=task.input,
            capabilities=context.capabilities,
            allowed_tools=tool_schemas,
            memories=memory_texts,
            tool_results=formatted_results,
            step_number=step_number,
        )
