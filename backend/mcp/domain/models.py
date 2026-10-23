"""
MCP Domain Models — Tool Contracts, Server Manifests, and Execution Payloads.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.mcp.domain.enums import MCPServerStatus, MCPToolRiskLevel


class MCPToolContract(BaseModel):
    """Declarative contract for a tool exposed by an MCP server."""

    tool_id: str = Field(description="Globally unique tool identifier, e.g., 'hrms.get_employee'")
    server_id: str = Field(description="Identifier of host MCP server")
    name: str = Field(description="Human readable name")
    description: str = Field(description="Purpose and semantics of the tool")
    input_schema: dict[str, Any] = Field(default_factory=dict, description="JSON Schema for input arguments")
    output_schema: dict[str, Any] = Field(default_factory=dict, description="JSON Schema for output response")
    required_capabilities: list[str] = Field(default_factory=list, description="Mandatory agent capability tokens")
    allowed_agents: list[str] = Field(default_factory=list, description="Whitelisted agent roles or '*' for all")
    risk_level: MCPToolRiskLevel = Field(default=MCPToolRiskLevel.LOW)
    requires_hitl: bool = Field(default=False)
    is_read_only: bool = Field(default=True)
    timeout_seconds: int = Field(default=15, ge=1, le=120)
    version: str = Field(default="1.0.0")


class MCPServerManifest(BaseModel):
    """Manifest describing an MCP server's identity, capabilities, and tools."""

    server_id: str
    name: str
    description: str
    version: str = "1.0.0"
    status: MCPServerStatus = MCPServerStatus.ONLINE
    tools: list[MCPToolContract] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    rate_limit_per_minute: int = 120
    timeout_seconds: int = 30
    registered_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class MCPToolCallRequest(BaseModel):
    """Standardized tool invocation payload preserving tenant and security context."""

    server_id: str
    tool_id: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    tenant_id: str
    actor_id: str
    agent_id: str
    task_id: str | None = None
    correlation_id: str | None = None
    security_context: dict[str, Any] = Field(default_factory=dict)


class MCPToolCallResponse(BaseModel):
    """Result of an MCP tool execution."""

    success: bool
    tool_id: str
    server_id: str
    result: Any = None
    error: str | None = None
    latency_ms: int = 0
    executed_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
