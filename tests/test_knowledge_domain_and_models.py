"""
Tests for Knowledge Domain Models and Entities.
"""

from __future__ import annotations

from backend.knowledge.domain.enums import (
    AccessScopeType,
    DocumentStatus,
    DocumentType,
    KnowledgeClassification,
    SourceType,
)
from backend.knowledge.domain.models import (
    CitationReference,
    KnowledgeAccessPolicy,
    KnowledgeAnswer,
    KnowledgeChunk,
    KnowledgeDocument,
)


def test_knowledge_document_instantiation():
    doc = KnowledgeDocument(
        organization_id="org-test-1",
        title="Employee Handbook 2026",
        source_type=SourceType.EMPLOYEE_HANDBOOK,
        document_type=DocumentType.HANDBOOK,
        classification=KnowledgeClassification.INTERNAL,
        owner_id="admin-1",
        checksum="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        storage_reference="storage://org-test-1/docs/handbook.pdf",
    )
    assert doc.document_id.startswith("doc-")
    assert doc.current_version == 1
    assert doc.status == DocumentStatus.UPLOADED
    assert doc.classification == KnowledgeClassification.INTERNAL


def test_knowledge_chunk_and_access_policy():
    chunk = KnowledgeChunk(
        document_id="doc-123",
        document_version=1,
        organization_id="org-test-1",
        chunk_index=0,
        content="Employees are entitled to 24 paid annual leave days per year.",
        token_count=11,
        char_length=62,
        section_title="Annual Leave Policy",
        page_number=4,
    )
    assert chunk.chunk_id.startswith("chk-")
    assert chunk.section_title == "Annual Leave Policy"

    policy = KnowledgeAccessPolicy(
        document_id="doc-123",
        organization_id="org-test-1",
        scope_type=AccessScopeType.ROLE_BASED,
        allowed_roles=["HR_ADMIN", "EMPLOYEE"],
    )
    assert policy.policy_id.startswith("kap-")
    assert "EMPLOYEE" in policy.allowed_roles


def test_knowledge_answer_and_citations():
    citation = CitationReference(
        document_id="doc-123",
        document_version=1,
        document_title="Leave Policy",
        section_title="Annual Leave",
        chunk_id="chk-abc",
        relevance_score=0.92,
        snippet="Employees get 24 paid leave days.",
    )
    ans = KnowledgeAnswer(
        answer="You are entitled to 24 paid annual leave days per year.",
        citations=[citation],
        confidence=0.95,
        abstain=False,
        retrieved_source_count=1,
    )
    assert ans.confidence == 0.95
    assert not ans.abstain
    assert len(ans.citations) == 1
    assert ans.citations[0].document_title == "Leave Policy"
