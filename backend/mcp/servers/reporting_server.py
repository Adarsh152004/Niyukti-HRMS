"""
Reporting MCP Server — Executive dashboard structure and summary export tools.
"""

from __future__ import annotations

from typing import Any

from backend.mcp.domain.models import MCPToolCallRequest, MCPToolContract
from backend.mcp.servers.base import MCPServer


class ReportingMCPServer(MCPServer):
    """Internal MCP server exposing executive reporting and tabular data preparation tools."""

    def __init__(self) -> None:
        super().__init__(
            server_id="reporting-server",
            name="Executive Reporting MCP Server",
            description="Assembles high-level KPI summaries, departmental health cards, and structured dashboard schemas.",
        )

    def _register_server_tools(self) -> None:
        self.register_tool(
            MCPToolContract(
                tool_id="reporting.build_executive_summary",
                server_id=self.server_id,
                name="Build Executive HR Summary",
                description="Compile high-level organizational HR health, hiring velocity, and retention index metrics.",
                input_schema={"type": "object", "properties": {"period_quarter": {"type": "string"}}},
                required_capabilities=["report:generate"],
                is_read_only=True,
            ),
            self._handle_summary,
        )

    async def _handle_summary(self, req: MCPToolCallRequest) -> dict[str, Any]:
        return {
            "period": req.arguments.get("period_quarter", "2026-Q3"),
            "retention_rate": 0.942,
            "offer_acceptance_rate": 0.885,
            "average_time_to_fill_days": 24,
            "overall_hr_health_score": "EXCELLENT",
        }
