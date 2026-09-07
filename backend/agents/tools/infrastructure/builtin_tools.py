"""
Built-in Tools Catalog — Standard read-only and command tool definitions.
"""

from __future__ import annotations

from backend.agents.tools.application.tool_registry import ToolRegistry
from backend.agents.tools.domain.enums import ToolCategory
from backend.agents.tools.domain.models import ToolDefinition


def register_builtin_tools(registry: ToolRegistry | None = None) -> None:
    """Register standard HRMS built-in tools into ToolRegistry."""
    target_registry = registry or ToolRegistry.get_instance()

    tools = [
        ToolDefinition(
            tool_id="employee.get",
            name="Get Employee Details",
            description="Retrieve detailed profile information for a specific employee ID.",
            category=ToolCategory.EMPLOYEE,
            resource="employee",
            action="read",
            required_capabilities=["employee:read"],
            risk_level="LOW",
            requires_hitl=False,
            command_type="employee.read",
            input_schema={
                "type": "object",
                "properties": {"employee_id": {"type": "string"}},
                "required": ["employee_id"],
            },
        ),
        ToolDefinition(
            tool_id="employee.list",
            name="List Employees",
            description="List employees for current organization with optional filters.",
            category=ToolCategory.EMPLOYEE,
            resource="employee",
            action="read",
            required_capabilities=["employee:read"],
            risk_level="LOW",
            requires_hitl=False,
            command_type="employee.list",
            input_schema={
                "type": "object",
                "properties": {"department_id": {"type": "string"}},
            },
        ),
        ToolDefinition(
            tool_id="department.get",
            name="Get Department Details",
            description="Retrieve department details by ID.",
            category=ToolCategory.DEPARTMENT,
            resource="department",
            action="read",
            required_capabilities=["department:read"],
            risk_level="LOW",
            requires_hitl=False,
            command_type="department.read",
            input_schema={
                "type": "object",
                "properties": {"department_id": {"type": "string"}},
                "required": ["department_id"],
            },
        ),
        ToolDefinition(
            tool_id="department.list",
            name="List Departments",
            description="List all organization departments.",
            category=ToolCategory.DEPARTMENT,
            resource="department",
            action="read",
            required_capabilities=["department:read"],
            risk_level="LOW",
            requires_hitl=False,
            command_type="department.list",
            input_schema={"type": "object", "properties": {}},
        ),
        ToolDefinition(
            tool_id="skill.get",
            name="Get Skill Details",
            description="Retrieve details for a specific skill.",
            category=ToolCategory.SKILL,
            resource="skill",
            action="read",
            required_capabilities=["skill:read"],
            risk_level="LOW",
            requires_hitl=False,
            command_type="skill.read",
            input_schema={
                "type": "object",
                "properties": {"skill_id": {"type": "string"}},
                "required": ["skill_id"],
            },
        ),
        ToolDefinition(
            tool_id="skill.list",
            name="List Skills",
            description="List all available skills.",
            category=ToolCategory.SKILL,
            resource="skill",
            action="read",
            required_capabilities=["skill:read"],
            risk_level="LOW",
            requires_hitl=False,
            command_type="skill.list",
            input_schema={"type": "object", "properties": {}},
        ),
    ]

    for tool in tools:
        target_registry.register_tool(tool)
