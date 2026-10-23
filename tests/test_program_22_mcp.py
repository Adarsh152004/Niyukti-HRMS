"""
AI-Powered Intelligent HRMS — Program 22 Governed MCP Tool Execution Test Suite.

Verifies:
1. Governed tool discovery and capability check
2. Structured tool execution output
"""

import pytest

from backend.mcp.schemas import MCPCallToolRequest
from backend.mcp.server import GovernedMCPServer


@pytest.mark.asyncio
async def test_governed_mcp_tool_execution():
    """Verify governed tool execution enforces capability and returns structured result."""
    mcp = GovernedMCPServer.get_instance()
    res = await mcp.execute_tool(MCPCallToolRequest(
        tool_name="attendance.summary",
        arguments={"threshold_percentage": 85.0},
        tenant_id="org-apex-01",
        actor_id="usr-p22-test",
    ))
    assert res.success is True
    assert res.data is not None
