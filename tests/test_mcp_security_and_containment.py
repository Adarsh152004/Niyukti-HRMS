"""
Tests for MCP Security, Isolation, Server Quarantining, and Prohibited Tool Rejection.
"""

from __future__ import annotations

import pytest

from backend.mcp.client.client import MCPClient
from backend.mcp.domain.enums import MCPServerStatus
from backend.mcp.servers.registry import MCPServerRegistry


@pytest.mark.asyncio
async def test_unregistered_mcp_tool_fails_safely():
    client = MCPClient.get_instance()

    resp = await client.call_tool(
        tool_id="non_existent.tool",
        arguments={},
        tenant_id="org-test",
        actor_id="actor-test",
        agent_id="agent-test",
    )
    assert not resp.success
    assert "not found" in resp.error.lower()


@pytest.mark.asyncio
async def test_quarantined_mcp_server_blocks_execution():
    client = MCPClient.get_instance()
    reg = MCPServerRegistry.get_instance()

    server = reg.get_server("analytics-server")
    assert server is not None

    try:
        # Quarantine the server
        server.status = MCPServerStatus.QUARANTINED

        resp = await client.call_tool(
            tool_id="analytics.get_headcount_stats",
            arguments={},
            tenant_id="org-test",
            actor_id="actor-test",
            agent_id="agent-test",
        )
        assert not resp.success
        assert "QUARANTINED" in resp.error
    finally:
        server.status = MCPServerStatus.ONLINE
