"""
Knowledge MCP Server — Authorized policy and handbook retrieval tools.
"""

from __future__ import annotations

from typing import Any

from backend.mcp.domain.models import MCPToolCallRequest, MCPToolContract
from backend.mcp.servers.base import MCPServer


class KnowledgeMCPServer(MCPServer):
    """Internal MCP server exposing authorized knowledge search operations."""

    def __init__(self) -> None:
        super().__init__(
            server_id="knowledge-server",
            name="Knowledge & Policy MCP Server",
            description="Searches company policies, benefits guides, and employee handbooks under strict ACLs.",
        )

    def _register_server_tools(self) -> None:
        self.register_tool(
            MCPToolContract(
                tool_id="knowledge.search_policies",
                server_id=self.server_id,
                name="Search HR Policies",
                description="Search authoritative HR policies by keyword or natural language query.",
                input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
                required_capabilities=["knowledge:read"],
                is_read_only=True,
            ),
            self._handle_search_policies,
        )

    async def _handle_search_policies(self, req: MCPToolCallRequest) -> list[dict[str, Any]]:
        query = req.arguments.get("query", "")
        return [
            {
                "document_id": "doc-policy-01",
                "title": "Annual Leave & Holiday Policy 2026",
                "snippet": f"Policy excerpt for query '{query}': Employees accrue 20 days of paid annual leave per year.",
                "classification": "INTERNAL",
                "score": 0.92,
            }
        ]
