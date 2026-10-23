"""
Tests for Multi-Provider AI Gateway, Model Routers, Circuit Breakers, and Tool Calling.
"""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from backend.ai.gateway.mock_provider import MockLLMProvider
from backend.ai.gateway.providers import (
    AnthropicProvider,
    GeminiProvider,
    LocalProvider,
    OpenAIProvider,
)
from backend.ai.gateway.router import AIGatewayRouter, RoutingTier


class SampleSchema(BaseModel):
    summary: str
    confidence: float


@pytest.mark.asyncio
async def test_all_provider_adapters_text_generation():
    providers = [
        MockLLMProvider(),
        OpenAIProvider(),
        AnthropicProvider(),
        GeminiProvider(),
        LocalProvider(),
    ]

    for p in providers:
        resp = await p.generate_text("Explain company annual leave entitlement.")
        assert resp.content is not None
        assert len(resp.content) > 0
        assert resp.provider == p.provider_name
        assert resp.usage.total_tokens > 0


@pytest.mark.asyncio
async def test_all_provider_adapters_structured_generation():
    providers = [
        MockLLMProvider(),
        OpenAIProvider(),
        AnthropicProvider(),
        GeminiProvider(),
        LocalProvider(),
    ]

    for p in providers:
        res = await p.generate_structured("Extract summary and score", SampleSchema)
        assert isinstance(res.data, SampleSchema)
        assert res.data.summary is not None
        assert res.data.confidence is not None


@pytest.mark.asyncio
async def test_all_provider_adapters_tool_calling():
    tools = [
        {"tool_id": "hrms.get_employee", "name": "hrms.get_employee", "default_args": {"employee_id": "emp-101"}},
    ]
    providers = [
        MockLLMProvider(),
        OpenAIProvider(),
        AnthropicProvider(),
        GeminiProvider(),
        LocalProvider(),
    ]

    for p in providers:
        res = await p.generate_tool_calls("Retrieve profile for hrms.get_employee", tools=tools)
        assert len(res.tool_calls) > 0
        assert res.tool_calls[0].tool_id == "hrms.get_employee"


@pytest.mark.asyncio
async def test_ai_gateway_router_cascade_and_telemetry():
    router = AIGatewayRouter.get_instance()
    org_id = "org-test-gateway"

    # 1. Text generation via router
    text_res = await router.generate_text(
        prompt="Analyze workforce metrics",
        organization_id=org_id,
        tier=RoutingTier.BALANCED,
    )
    assert text_res.content is not None

    # 2. Tool calling via router
    tools = [{"tool_id": "analytics.get_headcount_stats", "name": "analytics.get_headcount_stats"}]
    tool_res = await router.generate_tool_calls(
        prompt="Show analytics.get_headcount_stats for department",
        tools=tools,
        organization_id=org_id,
    )
    assert len(tool_res.tool_calls) > 0
