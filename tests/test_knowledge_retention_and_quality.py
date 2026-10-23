"""
Tests for Knowledge Retention Archival, Quality Reporting, and Evaluation Benchmark Suite.
"""

from __future__ import annotations

import pytest

from backend.knowledge.application.evaluation_service import BenchmarkTestCase, KnowledgeEvaluationService
from backend.knowledge.application.knowledge_service import KnowledgeService
from backend.knowledge.domain.enums import DocumentStatus
from backend.knowledge.domain.models import KnowledgeRetrievalQuery


@pytest.mark.asyncio
async def test_archival_and_vector_purge():
    svc = KnowledgeService.get_instance()
    org_id = "org-retention-test"

    doc = await svc.upload_and_index_document(
        organization_id=org_id,
        title="Temporary Vendor Protocol",
        content_bytes=b"Protocols for external contractors visiting office premise.",
        owner_id="admin-1",
    )

    # Verify search returns active document
    query = KnowledgeRetrievalQuery(
        query_text="contractors visiting office",
        organization_id=org_id,
        actor_id="admin-1",
        actor_roles=["ADMIN"],
    )
    active_results = await svc.retrieve_chunks(query)
    assert any(rc.chunk.document_id == doc.document_id for rc in active_results)

    # Archive document
    await svc.archive_document(org_id, doc.document_id, reason="Contract ended")
    assert doc.status == DocumentStatus.ARCHIVED

    # Subsequent active query must NOT return archived document
    after_archive_results = await svc.retrieve_chunks(query)
    assert not any(rc.chunk.document_id == doc.document_id for rc in after_archive_results)


@pytest.mark.asyncio
async def test_knowledge_quality_reporting():
    svc = KnowledgeService.get_instance()
    org_id = "org-quality-test"

    await svc.upload_and_index_document(
        organization_id=org_id,
        title="Standard Code of Ethics",
        content_bytes=b"Ethical standards and compliance reporting mechanisms.",
        owner_id="admin-1",
    )

    report = await svc.get_quality_report(org_id)
    assert report.total_documents >= 1
    assert report.quality_score >= 80.0


@pytest.mark.asyncio
async def test_evaluation_benchmark_suite():
    svc = KnowledgeService.get_instance()
    org_id = "org-eval-test"

    # Ingest document
    doc = await svc.upload_and_index_document(
        organization_id=org_id,
        title="Health and Safety Handbook",
        content_bytes=b"Fire safety protocols and emergency assembly point locations.",
        owner_id="admin-1",
    )

    eval_svc = KnowledgeEvaluationService(retrieval_service=svc.retrieval_service)

    test_cases = [
        BenchmarkTestCase(
            test_id="tc-001",
            query_text="Where is the emergency assembly point?",
            organization_id=org_id,
            actor_id="emp-1",
            actor_roles=["EMPLOYEE"],
            expected_document_ids=[doc.document_id],
            prohibited_document_ids=["doc-unauthorized-secret"],
        )
    ]

    metrics = await eval_svc.evaluate_benchmark_suite(test_cases)
    assert metrics.total_tests == 1
    assert metrics.hit_rate == 1.0
    assert metrics.unauthorized_retrieval_rate == 0.0
