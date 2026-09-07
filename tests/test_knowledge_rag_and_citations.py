"""
Tests for Knowledge RAG Synthesis, Citations, Prompt Firewall, and Abstention.
"""

from __future__ import annotations

import pytest

from backend.ai.gateway.mock_provider import MockLLMProvider
from backend.ai.gateway.router import AIGatewayRouter
from backend.knowledge.application.knowledge_service import KnowledgeService
from backend.knowledge.domain.enums import KnowledgeClassification, SourceType
from backend.knowledge.domain.models import KnowledgeRetrievalQuery


@pytest.mark.asyncio
async def test_rag_answer_generation_and_citations():
    svc = KnowledgeService.get_instance()
    org_id = "org-rag-test"

    # Setup Mock Provider with expected answer
    mock_prov = MockLLMProvider()
    mock_prov.set_mock_response(
        "Leave Policy",
        "Employees are entitled to 24 annual leave days and 10 sick leave days per calendar year.",
    )
    AIGatewayRouter.get_instance().register_provider(mock_prov, is_default=True)

    # Ingest leave policy
    await svc.upload_and_index_document(
        organization_id=org_id,
        title="Leave Policy",
        content_bytes=b"Employees are entitled to 24 annual leave days and 10 sick leave days per calendar year. Approvals are routed to reporting managers.",
        owner_id="admin-1",
        source_type=SourceType.HR_POLICY,
    )

    query = KnowledgeRetrievalQuery(
        query_text="How many annual leave days do I have per year?",
        organization_id=org_id,
        actor_id="emp-1",
        actor_roles=["EMPLOYEE"],
        top_k=3,
    )

    answer = await svc.answer_rag_query(query)
    assert answer.abstain is False
    assert answer.confidence > 0.8
    assert "24 annual leave days" in answer.answer
    assert len(answer.citations) > 0
    assert answer.citations[0].document_title == "Leave Policy"


@pytest.mark.asyncio
async def test_rag_abstention_when_unauthorized():
    svc = KnowledgeService.get_instance()
    org_id = "org-rag-test"

    # Ingest executive-only strategy
    await svc.upload_and_index_document(
        organization_id=org_id,
        title="CEO Strategic Restructuring Plan",
        content_bytes=b"Planned merger and departmental consolidations for Q4 2026.",
        owner_id="ceo-1",
        classification=KnowledgeClassification.EXECUTIVE_ONLY,
    )

    # Regular employee asks about executive strategy
    query = KnowledgeRetrievalQuery(
        query_text="What are the details of the CEO restructuring plan?",
        organization_id=org_id,
        actor_id="emp-99",
        actor_roles=["EMPLOYEE"],  # Not executive
        top_k=3,
    )

    answer = await svc.answer_rag_query(query)
    # MUST ABSTAIN due to lack of authorized sources
    assert answer.abstain is True
    assert answer.abstain_reason == "NO_AUTHORIZED_SOURCES"
    assert answer.retrieved_source_count == 0
