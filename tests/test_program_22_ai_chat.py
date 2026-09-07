"""
AI-Powered Intelligent HRMS — Program 22 AI Chat & Multi-Provider Test Suite.

Verifies:
1. Multi-Provider LLM Gateway
2. Structured Reasoning Output
"""

import pytest

from backend.ai.providers.base import LLMRouter


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
