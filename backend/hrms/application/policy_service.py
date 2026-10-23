"""
HR Policy Application Service — Policy document authoring, versioning, and compliance tracking.
"""

from __future__ import annotations

from collections.abc import Sequence

from backend.hrms.application.services import BaseApplicationService
from backend.hrms.domain.policy import HRPolicy, PolicyCategory, PolicyStatus
from backend.hrms.ports.repositories import PolicyRepository


class HRPolicyService(BaseApplicationService):
    """Deterministic organization-wide HR policy management."""

    def __init__(self, policy_repo: PolicyRepository) -> None:
        super().__init__()
        self.repo = policy_repo

    async def create_policy(
        self,
        organization_id: str,
        title: str,
        content: str,
        category: PolicyCategory = PolicyCategory.CODE_OF_CONDUCT,
        version: str = "1.0",
    ) -> HRPolicy:
        policy = HRPolicy(
            organization_id=organization_id,
            title=title,
            content=content,
            category=category,
            version=version,
            status=PolicyStatus.ACTIVE,
        )
        return await self.repo.create_policy(policy)

    async def get_policy(self, organization_id: str, policy_id: str) -> HRPolicy | None:
        return await self.repo.get_policy(organization_id, policy_id)

    async def list_policies(self, organization_id: str) -> Sequence[HRPolicy]:
        return await self.repo.list_policies(organization_id)
