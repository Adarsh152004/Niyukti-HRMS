"""
Tests for Extended AI Gateway Providers: Groq, Mistral, HuggingFace, OpenRouter, Cohere, Tavily, Supabase.
"""

from __future__ import annotations

import pytest

from backend.ai.gateway.providers import (
    CohereProvider,
    GroqProvider,
    HuggingFaceProvider,
    MistralProvider,
    OpenRouterProvider,
)
from backend.integrations.providers.supabase_storage import SupabaseStorageAdapter
from backend.integrations.providers.tavily_search import TavilySearchProvider


@pytest.mark.asyncio
async def test_all_extended_llm_providers():
    providers = [
        GroqProvider(),
        MistralProvider(),
        OpenRouterProvider(),
        HuggingFaceProvider(),
        CohereProvider(),
    ]

    for p in providers:
        # 1. Text generation
        res = await p.generate_text("Summarize statutory compliance rules.")
        assert res.content is not None
        assert p.provider_name in res.content.lower() or len(res.content) > 10

        # 2. Tool calling
        tools = [{"tool_id": "hrms.get_employee", "name": "hrms.get_employee"}]
        tool_res = await p.generate_tool_calls("Call hrms.get_employee", tools=tools)
        assert len(tool_res.tool_calls) > 0

        # 3. Text embedding
        emb = await p.embed_text("Employee handbook section 3")
        assert len(emb) == 128


@pytest.mark.asyncio
async def test_tavily_search_integration():
    tavily = TavilySearchProvider()
    resp = await tavily.search("statutory minimum wage regulations 2026")
    assert len(resp.results) > 0
    assert "https://" in resp.results[0].url
    assert resp.results[0].score > 0.5


@pytest.mark.asyncio
async def test_supabase_storage_integration():
    supabase = SupabaseStorageAdapter()
    sample_content = b"%PDF-1.4 sample employee offer letter content"

    # Upload
    meta = await supabase.upload_file(
        bucket="hr-documents",
        path="emp-101/offer_letter.pdf",
        content=sample_content,
        content_type="application/pdf",
    )
    assert meta.size_bytes == len(sample_content)
    assert meta.bucket == "hr-documents"
    assert meta.sha256_checksum is not None

    # Download
    retrieved = await supabase.download_file("hr-documents", "emp-101/offer_letter.pdf")
    assert retrieved == sample_content
