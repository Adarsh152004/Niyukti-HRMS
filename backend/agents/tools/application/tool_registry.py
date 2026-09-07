"""
Tool Registry — Registry managing structured tool definitions and safety checks.
"""

from __future__ import annotations

from collections.abc import Sequence

from backend.agents.tools.domain.exceptions import ToolNotFoundError, ToolValidationError
from backend.agents.tools.domain.models import ToolDefinition

PROHIBITED_TOOL_IDS = {
    "sql.execute",
    "raw_database_query",
    "arbitrary_python",
    "shell_execute",
    "unrestricted_http",
    "filesystem_write",
}


class ToolRegistry:
    """
    Registry for managing available tool definitions.
    Enforces security checks preventing registration of arbitrary Python/SQL execution tools.
    """

    _instance: ToolRegistry | None = None

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    @classmethod
    def get_instance(cls) -> ToolRegistry:
        if cls._instance is None:
            cls._instance = ToolRegistry()
            from backend.agents.tools.infrastructure.builtin_tools import register_builtin_tools

            register_builtin_tools(cls._instance)
        return cls._instance

    def register_tool(self, tool: ToolDefinition) -> ToolDefinition:
        """Register a new tool definition after safety verification."""
        if tool.tool_id in PROHIBITED_TOOL_IDS:
            raise ToolValidationError(f"Prohibited tool ID '{tool.tool_id}'. Direct SQL/Python/Shell tools are forbidden.")

        self._tools[tool.tool_id] = tool
        return tool

    def unregister_tool(self, tool_id: str) -> bool:
        """Unregister a tool definition."""
        if tool_id in self._tools:
            del self._tools[tool_id]
            return True
        return False

    def get_tool(self, tool_id: str) -> ToolDefinition:
        """Retrieve tool definition by ID."""
        tool = self._tools.get(tool_id)
        if not tool or not tool.enabled:
            raise ToolNotFoundError(f"Tool '{tool_id}' not found or disabled.")
        return tool

    def list_tools(self) -> Sequence[ToolDefinition]:
        """List all enabled tools."""
        return [t for t in self._tools.values() if t.enabled]
