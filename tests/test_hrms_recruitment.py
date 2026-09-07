"""
Tests for Deterministic Recruitment ATS Service: Requisitions and Candidate Pipeline.
"""

from __future__ import annotations

import pytest

from backend.hrms.application.recruitment_service import RecruitmentService
from backend.hrms.domain.recruitment import CandidateSource, RequisitionStatus
from backend.hrms.infrastructure.memory_repositories import InMemoryRecruitmentRepository


@pytest.mark.asyncio
async def test_recruitment_requisition_and_candidate_pipeline():
    repo = InMemoryRecruitmentRepository()
    svc = RecruitmentService(repo)
    org_id = "org-recruitment-test"

    # 1. Create requisition
    req = await svc.create_requisition(
        organization_id=org_id,
        title="Senior AI Platform Engineer",
        department_id="dept-eng-01",
        headcount=2,
        job_description="Architect autonomous agents and deterministic systems.",
        min_salary=120000.0,
        max_salary=160000.0,
    )
    assert req.title == "Senior AI Platform Engineer"
    assert req.status == RequisitionStatus.APPROVED

    # 2. Add candidate
    cand = await svc.add_candidate(
        organization_id=org_id,
        first_name="Jordan",
        last_name="Lee",
        email="jordan.lee@example.com",
        source=CandidateSource.LINKEDIN,
        years_of_experience=6.5,
    )
    assert cand.first_name == "Jordan"
    assert cand.email == "jordan.lee@example.com"

    # 3. List
    reqs = await svc.list_requisitions(org_id)
    cands = await svc.list_candidates(org_id)
    assert len(reqs) == 1
    assert len(cands) == 1
