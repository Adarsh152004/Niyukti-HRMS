"""
Recruitment ATS Application Service — Requisitions, candidate pipelines, and deterministic hiring workflows.
"""

from __future__ import annotations

from collections.abc import Sequence

from backend.hrms.application.services import BaseApplicationService
from backend.hrms.domain.recruitment import Candidate, CandidateSource, JobRequisition, RequisitionStatus
from backend.hrms.ports.repositories import RecruitmentRepository


class RecruitmentService(BaseApplicationService):
    """Deterministic ATS pipeline management."""

    def __init__(self, recruitment_repo: RecruitmentRepository) -> None:
        super().__init__()
        self.repo = recruitment_repo

    async def create_requisition(
        self,
        organization_id: str,
        title: str,
        department_id: str,
        headcount: int = 1,
        job_description: str = "",
        min_salary: float | None = None,
        max_salary: float | None = None,
    ) -> JobRequisition:
        req = JobRequisition(
            organization_id=organization_id,
            title=title,
            department_id=department_id,
            headcount=headcount,
            job_description=job_description,
            min_salary=min_salary,
            max_salary=max_salary,
            status=RequisitionStatus.APPROVED,
        )
        return await self.repo.create_requisition(req)

    async def add_candidate(
        self,
        organization_id: str,
        first_name: str,
        last_name: str,
        email: str,
        source: CandidateSource = CandidateSource.DIRECT_APPLY,
        phone: str | None = None,
        years_of_experience: float | None = None,
    ) -> Candidate:
        cand = Candidate(
            organization_id=organization_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            source=source,
            phone=phone,
            years_of_experience=years_of_experience,
        )
        return await self.repo.create_candidate(cand)

    async def list_requisitions(self, organization_id: str) -> Sequence[JobRequisition]:
        return await self.repo.list_requisitions(organization_id)

    async def list_candidates(self, organization_id: str) -> Sequence[Candidate]:
        return await self.repo.list_candidates(organization_id)
