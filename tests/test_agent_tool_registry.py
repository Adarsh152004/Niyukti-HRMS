"""Tests — Agent ToolRegistry registration, lookups, and prohibited tool rejection."""

import pytest

from backend.agents.tools.application.tool_registry import ToolRegistry
from backend.agents.tools.domain.enums import ToolCategory
from backend.agents.tools.domain.exceptions import ToolValidationError
from backend.agents.tools.domain.models import ToolDefinition
from backend.agents.tools.infrastructure.builtin_tools import register_builtin_tools


def test_tool_registry_registration_and_lookup():
    registry = ToolRegistry()
    register_builtin_tools(registry)

    tool = registry.get_tool("employee.get")
    assert tool.name == "Get Employee Details"
    assert tool.category == ToolCategory.EMPLOYEE
    assert "employee:read" in tool.required_capabilities


def test_prohibited_tools_registration_rejected():
    registry = ToolRegistry()

    prohibited_tool = ToolDefinition(
        tool_id="sql.execute",
        name="Execute SQL Query",
        description="Run raw SQL query",
        category=ToolCategory.CUSTOM,
        resource="database",
        action="execute",
        command_type="sql.execute",
    )

    with pytest.raises(ToolValidationError, match="Prohibited tool ID"):
        registry.register_tool(prohibited_tool)
