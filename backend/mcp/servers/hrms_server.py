"""
HRMS MCP Server — Provides employee, department, and organization profile tools.
"""

from __future__ import annotations

from typing import Any

from backend.mcp.domain.models import MCPToolCallRequest, MCPToolContract
from backend.mcp.servers.base import MCPServer


class HRMSMCPServer(MCPServer):
    """Internal MCP server exposing core deterministic HRMS data read operations."""

    def __init__(self) -> None:
        super().__init__(
            server_id="hrms-server",
            name="HRMS Core MCP Server",
            description="Authoritative read-only queries for employee records, department structures, and designations.",
        )

    def _register_server_tools(self) -> None:
        self.register_tool(
            MCPToolContract(
                tool_id="hrms.get_employee",
                server_id=self.server_id,
                name="Get Employee Details",
                description="Retrieve core employee details by employee ID.",
                input_schema={"type": "object", "properties": {"employee_id": {"type": "string"}}, "required": ["employee_id"]},
                required_capabilities=["employee:read"],
                is_read_only=True,
            ),
            self._handle_get_employee,
        )
        self.register_tool(
            MCPToolContract(
                tool_id="hrms.list_employees",
                server_id=self.server_id,
                name="List Employees",
                description="List employees within the authorized department or organization.",
                input_schema={"type": "object", "properties": {"department_id": {"type": "string"}}},
                required_capabilities=["employee:read"],
                is_read_only=True,
            ),
            self._handle_list_employees,
        )

    async def _handle_get_employee(self, req: MCPToolCallRequest) -> dict[str, Any]:
        emp_id = req.arguments.get("employee_id", "emp-default")
        return {
            "employee_id": emp_id,
            "organization_id": req.tenant_id,
            "first_name": "Alex",
            "last_name": "Taylor",
            "email": f"{emp_id}@example-corp.com",
            "department": "Engineering",
            "designation": "Senior Staff Engineer",
            "employment_status": "ACTIVE",
        }

    async def _handle_list_employees(self, req: MCPToolCallRequest) -> list[dict[str, Any]]:
        dept_id = req.arguments.get("department_id", "dept-all")
        return [
            {
                "employee_id": f"emp-00{i}",
                "organization_id": req.tenant_id,
                "name": f"Employee {i}",
                "department_id": dept_id,
                "status": "ACTIVE",
            }
            for i in range(1, 4)
        ]
