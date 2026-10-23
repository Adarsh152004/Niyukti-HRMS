"""
Approval Inbox Application Service — Unified multi-entity HITL approval workflow.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from backend.hrms.application.services import BaseApplicationService
from backend.hrms.domain.approvals import ApprovalDecision, ApprovalRequest, ApprovalStatus, ApprovalType
from backend.hrms.domain.common import utc_now
from backend.hrms.ports.repositories import ApprovalRepository


class ApprovalInboxService(BaseApplicationService):
    """Centralized HITL approval processing for all HRMS domains."""

    def __init__(self, approval_repo: ApprovalRepository) -> None:
        super().__init__()
        self.repo = approval_repo

    async def submit_request(
        self,
        organization_id: str,
        approval_type: ApprovalType,
        requester_id: str,
        requester_role: str,
        target_entity_id: str,
        payload: dict[str, Any] | None = None,
        risk_level: str = "MEDIUM",
    ) -> ApprovalRequest:
        req = ApprovalRequest(
            organization_id=organization_id,
            approval_type=approval_type,
            requester_id=requester_id,
            requester_role=requester_role,
            target_entity_id=target_entity_id,
            payload=payload or {},
            risk_level=risk_level,
            status=ApprovalStatus.PENDING,
        )
        return await self.repo.create(req)

    async def decide_request(
        self,
        organization_id: str,
        approval_id: str,
        approver_id: str,
        approver_role: str,
        decision: str,
        rejection_reason: str | None = None,
    ) -> ApprovalRequest | None:
        req = await self.repo.get_by_id(organization_id, approval_id)
        if not req or req.status != ApprovalStatus.PENDING:
            return None

        status = ApprovalStatus.APPROVED if decision.upper() == "APPROVED" else ApprovalStatus.REJECTED
        dec = ApprovalDecision(
            approver_id=approver_id,
            approver_role=approver_role,
            decision=decision.upper(),
            rejection_reason=rejection_reason,
        )
        req.status = status
        req.decisions.append(dec)
        req.updated_at = utc_now()
        return await self.repo.update(req)

    async def list_pending(self, organization_id: str) -> Sequence[ApprovalRequest]:
        return await self.repo.list_pending(organization_id)
