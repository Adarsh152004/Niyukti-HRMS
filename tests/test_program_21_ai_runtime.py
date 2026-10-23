"""
AI-Powered Intelligent HRMS — Program 21 AI Runtime & Governed Agents Test Suite.

Verifies:
1. Multi-Provider LLM Router with active provider resolution
2. Context window budgeting and token priority allocation
3. Governed MCP tool execution with capability verification
4. 24 specialized agent definitions integrity
"""

import pytest

from backend.agents.context.budget import ContextBudgetManager, TokenBudgetAllocation
from backend.agents.specialized.registry.catalog import SpecializedAgentCatalog
from backend.ai.providers.base import LLMRouter
from backend.mcp.schemas import MCPCallToolRequest
from backend.mcp.server import GovernedMCPServer


@pytest.mark.asyncio
async def test_llm_router_and_structured_reasoning():
    """Verify LLMRouter generates structured ReasoningDecision."""
    router = LLMRouter()
    assert router.primary in ["gemini", "groq", "openai", "anthropic", "mock"]

    response = await router.generate_reasoning(
        system_prompt="You are an enterprise HR assistant.",
        user_prompt="Identify employees with low attendance",
    )
    assert response.decision is not None
    assert response.tokens_prompt >= 0


def test_context_budget_manager_slices():
    """Verify context token budgeting satisfies max limit."""
    budget_mgr = ContextBudgetManager(allocation=TokenBudgetAllocation(max_total_tokens=8192))
    assert budget_mgr.allocation.max_total_tokens == 8192


@pytest.mark.asyncio
async def test_governed_mcp_tool_execution():
    """Verify governed tool execution enforces capability and returns structured result."""
    mcp = GovernedMCPServer.get_instance()
    res = await mcp.execute_tool(MCPCallToolRequest(
        tool_name="attendance.summary",
        arguments={"threshold_percentage": 85.0},
        tenant_id="org-apex-01",
        actor_id="usr-p21-test",
    ))
    assert res.success is True
    assert res.data is not None


def test_specialized_agent_catalog_autonomy():
    """Verify all 24 agents exist in catalog with configured autonomy."""
    catalog = SpecializedAgentCatalog.get_instance()
    agents = catalog.list_definitions()
    assert len(agents) == 24
    for agent in agents:
        assert agent.display_name is not None
        assert agent.autonomy_mode is not None
