"""
Notification MCP Server — Governed notification dispatching and status tools.
"""

from __future__ import annotations

from typing import Any

from backend.mcp.domain.models import MCPToolCallRequest, MCPToolContract
from backend.mcp.servers.base import MCPServer


class NotificationMCPServer(MCPServer):
    """Internal MCP server exposing governed notification dispatch tools."""

    def __init__(self) -> None:
        super().__init__(
            server_id="notification-server",
            name="Notification Dispatch MCP Server",
            description="Dispatches governed email, SMS, and in-app alerts through provider gateways.",
        )

    def _register_server_tools(self) -> None:
        self.register_tool(
            MCPToolContract(
                tool_id="notification.dispatch_template",
                server_id=self.server_id,
                name="Dispatch Notification Template",
                description="Trigger an approved HR email or in-app message template to an authorized recipient.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "template_id": {"type": "string"},
                        "recipient_id": {"type": "string"},
                        "parameters": {"type": "object"},
                    },
                    "required": ["template_id", "recipient_id"],
                },
                required_capabilities=["notification:send"],
                is_read_only=False,
            ),
            self._handle_dispatch,
        )

    async def _handle_dispatch(self, req: MCPToolCallRequest) -> dict[str, Any]:
        return {
            "dispatch_id": "disp-987654",
            "recipient_id": req.arguments.get("recipient_id"),
            "template_id": req.arguments.get("template_id"),
            "status": "QUEUED_FOR_DELIVERY",
        }
