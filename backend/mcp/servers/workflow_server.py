"""
Workflow MCP Server — Workflow status inspection and task queue tools.
"""

from __future__ import annotations

from typing import Any

from backend.mcp.domain.models import MCPToolCallRequest, MCPToolContract
from backend.mcp.servers.base import MCPServer


class WorkflowMCPServer(MCPServer):
    """Internal MCP server exposing workflow tracking and task status inspection."""

    def __init__(self) -> None:
        super().__init__(
            server_id="workflow-server",
            name="Workflow Engine MCP Server",
            description="Inspects active workflow executions, step progressions, and pending human tasks.",
        )

    def _register_server_tools(self) -> None:
        self.register_tool(
            MCPToolContract(
                tool_id="workflow.get_instance_status",
                server_id=self.server_id,
                name="Get Workflow Status",
                description="Query the real-time execution state of a specific workflow instance.",
                input_schema={"type": "object", "properties": {"workflow_id": {"type": "string"}}, "required": ["workflow_id"]},
                required_capabilities=["workflow:read"],
                is_read_only=True,
            ),
            self._handle_get_status,
        )

    async def _handle_get_status(self, req: MCPToolCallRequest) -> dict[str, Any]:
        wf_id = req.arguments.get("workflow_id", "wf-default")
        return {
            "workflow_id": wf_id,
            "organization_id": req.tenant_id,
            "workflow_type": "EMPLOYEE_ONBOARDING",
            "status": "IN_PROGRESS",
            "current_step": "step_create_email_account",
            "completed_steps": ["step_create_profile", "step_assign_manager"],
            "pending_steps": ["step_order_laptop", "step_welcome_orientation"],
        }
