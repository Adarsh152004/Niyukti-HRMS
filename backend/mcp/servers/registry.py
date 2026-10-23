"""
MCP Server Registry — Central catalog managing internal and external MCP servers.
"""

from __future__ import annotations

import logging

from backend.mcp.domain.enums import MCPServerStatus
from backend.mcp.domain.models import MCPServerManifest, MCPToolContract
from backend.mcp.servers.analytics_server import AnalyticsMCPServer
from backend.mcp.servers.base import MCPServer
from backend.mcp.servers.document_server import DocumentMCPServer
from backend.mcp.servers.hrms_server import HRMSMCPServer
from backend.mcp.servers.knowledge_server import KnowledgeMCPServer
from backend.mcp.servers.notification_server import NotificationMCPServer
from backend.mcp.servers.payroll_server import PayrollMCPServer
from backend.mcp.servers.recruitment_server import RecruitmentMCPServer
from backend.mcp.servers.reporting_server import ReportingMCPServer
from backend.mcp.servers.workflow_server import WorkflowMCPServer

logger = logging.getLogger(__name__)


class MCPServerRegistry:
    """
    Central catalog of all MCP servers within the HRMS ecosystem.
    Maintains server health, tool registries, and dispatch routing.
    """

    _instance: MCPServerRegistry | None = None

    def __init__(self) -> None:
        self._servers: dict[str, MCPServer] = {}
        self._register_default_servers()

    @classmethod
    def get_instance(cls) -> MCPServerRegistry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _register_default_servers(self) -> None:
        """Register the 9 standard internal MCP servers."""
        default_servers: list[MCPServer] = [
            HRMSMCPServer(),
            KnowledgeMCPServer(),
            AnalyticsMCPServer(),
            WorkflowMCPServer(),
            DocumentMCPServer(),
            RecruitmentMCPServer(),
            PayrollMCPServer(),
            NotificationMCPServer(),
            ReportingMCPServer(),
        ]
        for s in default_servers:
            self.register_server(s)

    def register_server(self, server: MCPServer) -> None:
        """Register a new MCP server in the ecosystem."""
        self._servers[server.server_id] = server
        logger.info(f"Registered MCP Server [{server.server_id}] with version [{server.version}]")

    def get_server(self, server_id: str) -> MCPServer | None:
        """Retrieve server instance by ID."""
        return self._servers.get(server_id)

    def list_servers(self) -> list[MCPServerManifest]:
        """List manifests of all registered servers."""
        return [s.get_manifest() for s in self._servers.values()]

    def list_all_tools(self) -> list[MCPToolContract]:
        """List all tools available across all healthy MCP servers."""
        tools: list[MCPToolContract] = []
        for s in self._servers.values():
            if s.status == MCPServerStatus.ONLINE:
                tools.extend(s.get_manifest().tools)
        return tools

    def find_tool(self, tool_id: str) -> tuple[MCPServer | None, MCPToolContract | None]:
        """Find the hosting server and tool contract for a given tool_id."""
        for s in self._servers.values():
            manifest = s.get_manifest()
            for t in manifest.tools:
                if t.tool_id == tool_id:
                    return s, t
        return None, None
