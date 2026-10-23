"""
Analytics MCP Server — Aggregated metrics and HR KPI query tools.
"""

from __future__ import annotations

from typing import Any

from backend.mcp.domain.models import MCPToolCallRequest, MCPToolContract
from backend.mcp.servers.base import MCPServer


class AnalyticsMCPServer(MCPServer):
    """Internal MCP server exposing read-only aggregated HR metrics and KPI computations."""

    def __init__(self) -> None:
        super().__init__(
            server_id="analytics-server",
            name="HR Analytics MCP Server",
            description="Computes and retrieves aggregated headcount, turnover rates, and departmental metrics.",
        )

    def _register_server_tools(self) -> None:
        self.register_tool(
            MCPToolContract(
                tool_id="analytics.get_headcount_stats",
                server_id=self.server_id,
                name="Get Headcount Statistics",
                description="Retrieve aggregated headcount distribution across departments.",
                input_schema={"type": "object", "properties": {"organization_id": {"type": "string"}}},
                required_capabilities=["analytics:read"],
                is_read_only=True,
            ),
            self._handle_headcount_stats,
        )

    async def _handle_headcount_stats(self, req: MCPToolCallRequest) -> dict[str, Any]:
        return {
            "organization_id": req.tenant_id,
            "total_headcount": 1250,
            "active_count": 1220,
            "on_leave_count": 30,
            "department_breakdown": {
                "Engineering": 550,
                "Sales & Marketing": 320,
                "HR & Operations": 180,
                "Finance": 200,
            },
        }
