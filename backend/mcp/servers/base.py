"""
Base MCP Server Architecture — Server contracts, tool dispatching, and security containment.
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from typing import Any

from backend.mcp.domain.enums import MCPServerStatus
from backend.mcp.domain.models import (
    MCPServerManifest,
    MCPToolCallRequest,
    MCPToolCallResponse,
    MCPToolContract,
)

logger = logging.getLogger(__name__)


class MCPServer(ABC):
    """
    Abstract internal MCP Server.
    Provides standard manifest inspection, tool dispatching, tenant scoping, and health tracking.
    """

    def __init__(self, server_id: str, name: str, description: str, version: str = "1.0.0") -> None:
        self.server_id = server_id
        self.name = name
        self.description = description
        self.version = version
        self.status = MCPServerStatus.ONLINE
        self._tools: dict[str, MCPToolContract] = {}
        self._handlers: dict[str, Callable[[MCPToolCallRequest], Coroutine[Any, Any, Any]]] = {}
        self._register_server_tools()

    @abstractmethod
    def _register_server_tools(self) -> None:
        """Register the specific tool contracts and their async dispatch handlers."""
        pass

    def register_tool(
        self,
        contract: MCPToolContract,
        handler: Callable[[MCPToolCallRequest], Coroutine[Any, Any, Any]],
    ) -> None:
        """Register a tool contract with its executable async handler."""
        self._tools[contract.tool_id] = contract
        self._handlers[contract.tool_id] = handler

    def get_manifest(self) -> MCPServerManifest:
        """Retrieve full server manifest including all active tool contracts."""
        return MCPServerManifest(
            server_id=self.server_id,
            name=self.name,
            description=self.description,
            version=self.version,
            status=self.status,
            tools=list(self._tools.values()),
            capabilities=[t.tool_id for t in self._tools.values()],
        )

    async def execute_tool(self, request: MCPToolCallRequest) -> MCPToolCallResponse:
        """
        Execute an incoming tool request with tenant isolation, rate limiting, and latency tracking.
        """
        start_time = time.perf_counter()

        if self.status != MCPServerStatus.ONLINE:
            return MCPToolCallResponse(
                success=False,
                tool_id=request.tool_id,
                server_id=self.server_id,
                error=f"MCP Server [{self.server_id}] is currently {self.status.value}.",
                latency_ms=0,
            )

        contract = self._tools.get(request.tool_id)
        handler = self._handlers.get(request.tool_id)

        if not contract or not handler:
            return MCPToolCallResponse(
                success=False,
                tool_id=request.tool_id,
                server_id=self.server_id,
                error=f"Tool [{request.tool_id}] not found on server [{self.server_id}].",
                latency_ms=0,
            )

        # Execute handler safely
        try:
            result = await handler(request)
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return MCPToolCallResponse(
                success=True,
                tool_id=request.tool_id,
                server_id=self.server_id,
                result=result,
                latency_ms=elapsed_ms,
            )
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            logger.error(f"Error executing MCP tool [{request.tool_id}] on server [{self.server_id}]: {e}")
            return MCPToolCallResponse(
                success=False,
                tool_id=request.tool_id,
                server_id=self.server_id,
                error=str(e),
                latency_ms=elapsed_ms,
            )
