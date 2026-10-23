"""
MCP Client — High-level client for discovering, inspecting, and invoking tools across MCP servers.
"""

from __future__ import annotations

import logging
from typing import Any

from backend.mcp.domain.enums import MCPServerStatus
from backend.mcp.domain.models import (
    MCPServerManifest,
    MCPToolCallRequest,
    MCPToolCallResponse,
    MCPToolContract,
)
from backend.mcp.servers.registry import MCPServerRegistry

logger = logging.getLogger(__name__)


class MCPClient:
    """
    Client for interacting with MCP servers.
    Preserves tenant boundaries, agent identities, and security contexts across tool invocations.
    """

    _instance: MCPClient | None = None

    def __init__(self, registry: MCPServerRegistry | None = None) -> None:
        self.registry = registry or MCPServerRegistry.get_instance()

    @classmethod
    def get_instance(cls) -> MCPClient:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def discover_servers(self) -> list[MCPServerManifest]:
        """Discover all registered MCP servers and their manifests."""
        return self.registry.list_servers()

    async def discover_tools(self) -> list[MCPToolContract]:
        """Discover all available tools across healthy MCP servers."""
        return self.registry.list_all_tools()

    async def inspect_tool_schema(self, tool_id: str) -> dict[str, Any] | None:
        """Retrieve the JSON schema for a specific tool's arguments."""
        _, contract = self.registry.find_tool(tool_id)
        if contract:
            return contract.input_schema
        return None

    async def call_tool(
        self,
        tool_id: str,
        arguments: dict[str, Any],
        tenant_id: str,
        actor_id: str,
        agent_id: str,
        task_id: str | None = None,
        correlation_id: str | None = None,
        security_context: dict[str, Any] | None = None,
    ) -> MCPToolCallResponse:
        """
        Invoke an MCP tool, passing full provenance, tenant isolation, and security contexts.
        """
        server, contract = self.registry.find_tool(tool_id)
        if not server or not contract:
            return MCPToolCallResponse(
                success=False,
                tool_id=tool_id,
                server_id="unknown",
                error=f"MCP tool [{tool_id}] not found in any registered server.",
                latency_ms=0,
            )

        # Enforce server health check
        if server.status != MCPServerStatus.ONLINE:
            return MCPToolCallResponse(
                success=False,
                tool_id=tool_id,
                server_id=server.server_id,
                error=f"MCP server [{server.server_id}] is currently {server.status.value}.",
                latency_ms=0,
            )

        request = MCPToolCallRequest(
            server_id=server.server_id,
            tool_id=tool_id,
            arguments=arguments,
            tenant_id=tenant_id,
            actor_id=actor_id,
            agent_id=agent_id,
            task_id=task_id,
            correlation_id=correlation_id,
            security_context=security_context or {},
        )

        return await server.execute_tool(request)
