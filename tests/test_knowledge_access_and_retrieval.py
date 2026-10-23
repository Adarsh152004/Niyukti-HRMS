"""
Tests for Pre-Retrieval Authorization, Scope Constraints, and Tenant Isolation.
"""

from __future__ import annotations

import pytest

from backend.knowledge.application.knowledge_service import KnowledgeService
from backend.knowledge.domain.enums import KnowledgeClassification
from backend.knowledge.domain.models import KnowledgeRetrievalQuery


@pytest.mark.asyncio
async def test_pre_retrieval_authorization_and_role_scoping():
    svc = KnowledgeService.get_instance()
    org_id = "org-access-test"

    # 1. Ingest Public Handbook (Accessible by all employees)
    doc_public = await svc.upload_and_index_document(
        organization_id=org_id,
        title="General Employee Handbook",
        content_bytes=b"General workplace rules, dress code, and office holidays.",
        owner_id="admin-1",
        classification=KnowledgeClassification.INTERNAL,
    )

    # 2. Ingest HR-Only Policy (Restricted)
    doc_hr = await svc.upload_and_index_document(
        organization_id=org_id,
        title="Executive Compensation and Bonus Guidelines",
        content_bytes=b"Confidential formula for executive equity grants and severance packages.",
        owner_id="admin-1",
        classification=KnowledgeClassification.HR_ONLY,
    )

    # Regular employee query
    emp_query = KnowledgeRetrievalQuery(
        query_text="holidays and dress code",
        organization_id=org_id,
        actor_id="emp-101",
        actor_roles=["EMPLOYEE"],
        top_k=5,
    )
    emp_results = await svc.retrieve_chunks(emp_query)
    emp_doc_ids = {rc.chunk.document_id for rc in emp_results}

    # Employee CAN retrieve public handbook
    assert doc_public.document_id in emp_doc_ids
    # Employee CANNOT retrieve HR-only compensation document
    assert doc_hr.document_id not in emp_doc_ids

    # HR Manager query
    hr_query = KnowledgeRetrievalQuery(
        query_text="executive bonus guidelines",
        organization_id=org_id,
        actor_id="hr-mgr-201",
        actor_roles=["HR_MANAGER"],
        top_k=5,
    )
    hr_results = await svc.retrieve_chunks(hr_query)
    hr_doc_ids = {rc.chunk.document_id for rc in hr_results}

    # HR Manager CAN retrieve HR-only document
    assert doc_hr.document_id in hr_doc_ids


@pytest.mark.asyncio
async def test_strict_tenant_isolation_retrieval():
    svc = KnowledgeService.get_instance()
    org_a = "org-tenant-alpha"
    org_b = "org-tenant-beta"

    # Ingest document into Tenant Alpha
    doc_a = await svc.upload_and_index_document(
        organization_id=org_a,
        title="Alpha Proprietary Roadmap",
        content_bytes=b"Confidential technology roadmap for Tenant Alpha.",
        owner_id="admin-alpha",
        classification=KnowledgeClassification.INTERNAL,
    )

    # Actor from Tenant Beta queries for roadmap
    query_b = KnowledgeRetrievalQuery(
        query_text="technology roadmap",
        organization_id=org_b,
        actor_id="user-beta",
        actor_roles=["ADMIN"],
        top_k=5,
    )
    results_b = await svc.retrieve_chunks(query_b)

    # MUST NEVER retrieve Tenant Alpha's document
    assert not any(rc.chunk.document_id == doc_a.document_id for rc in results_b)
    assert not any(rc.chunk.organization_id == org_a for rc in results_b)
