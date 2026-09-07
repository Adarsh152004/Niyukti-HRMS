"""
Tests for MCP Client, Tool Discovery, and Governed Execution.
"""

from __future__ import annotations

import pytest

from backend.mcp.client.client import MCPClient


@pytest.mark.asyncio
async def test_mcp_client_server_discovery():
    client = MCPClient.get_instance()

    servers = await client.discover_servers()
    assert len(servers) >= 9

    server_ids = [s.server_id for s in servers]
    assert "hrms-server" in server_ids
    assert "knowledge-server" in server_ids
    assert "analytics-server" in server_ids
    assert "payroll-server" in server_ids


@pytest.mark.asyncio
async def test_mcp_client_tool_enumeration_and_invocation():
    client = MCPClient.get_instance()
    tenant_id = "org-mcp-test"

    # 1. Discover all tools
    tools = await client.discover_tools()
    assert len(tools) >= 9

    # 2. Inspect schema
    schema = await client.inspect_tool_schema("hrms.get_employee")
    assert schema is not None
    assert "properties" in schema

    # 3. Call tool
    res = await client.call_tool(
        tool_id="hrms.get_employee",
        arguments={"employee_id": "emp-999"},
        tenant_id=tenant_id,
        actor_id="actor-test",
        agent_id="agent-test",
    )
    assert res.success is True
    assert res.result["employee_id"] == "emp-999"
    assert res.result["organization_id"] == tenant_id
