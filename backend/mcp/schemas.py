"""
AI-Powered Intelligent HRMS — Model Context Protocol (MCP) Schemas.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class MCPToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    resource: str
    action: str
    required_capability: str
    risk_level: str = "LOW"
    requires_hitl: bool = False
    allowed_agents: list[str] = Field(default_factory=lambda: ["*"])


class MCPCallToolRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    tenant_id: str
    actor_id: str
    actor_roles: list[str] = Field(default_factory=list)
    agent_id: str | None = None


class MCPCallToolResponse(BaseModel):
    tool_name: str
    success: bool
    data: Any | None = None
    error: str | None = None
    requires_approval: bool = False
    approval_request_id: str | None = None
