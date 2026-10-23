"""
Tool Discovery — Capability-Aware Tool Discovery Service.
"""

from __future__ import annotations

from collections.abc import Sequence

from backend.agents.domain.models import Agent, AgentExecutionContext
from backend.agents.tools.application.tool_registry import ToolRegistry
from backend.agents.tools.domain.models import ToolDefinition


class ToolDiscovery:
    """
    Capability-aware tool discovery engine.
    Ensures AI Agents only discover tools matching their declared capabilities.
    """

    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.registry = registry or ToolRegistry.get_instance()

    def discover_tools(self, agent: Agent, context: AgentExecutionContext) -> Sequence[ToolDefinition]:
        """
        Filter registered tools to return ONLY those matching agent capabilities and agent type.
        """
        all_tools = self.registry.list_tools()
        visible_tools: list[ToolDefinition] = []

        for tool in all_tools:
            # 1. Agent capability check
            if not agent.has_capability(tool.resource, tool.action):
                continue

            # 2. Allowed Agent Types filter (if specified)
            if tool.allowed_agent_types and agent.agent_type.value not in tool.allowed_agent_types:
                continue

            visible_tools.append(tool)

        return visible_tools
