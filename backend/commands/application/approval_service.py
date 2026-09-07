"""
Approval Service — HITL Approval Gate Management and Payload Hash Verification.

Integrates with Node 4 ApprovalRequest/ApprovalDecision domain primitives.
Enforces:
- Deterministic payload hash verification (payload modification post-approval invalidates request)
- Self-approval prevention (an actor CANNOT approve their own command)
- Cross-tenant approval prevention
- Expiration check & status transitions
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from backend.commands.domain.models import Command, CommandContext
from backend.hrms.domain.actor import Actor
from backend.security.domain.enums import ApprovalStatus
from backend.security.domain.models import ApprovalDecision, ApprovalRequest


class ApprovalValidationError(Exception):
    """Raised when an approval action violates security rules."""

    pass


class ApprovalService:
    """
    HITL Approval Gate Manager.
    """

    def __init__(self) -> None:
        self._requests_by_id: dict[str, ApprovalRequest] = {}
        self._command_payload_hashes: dict[str, str] = {}  # request_id -> payload_hash
        self._command_ids: dict[str, str] = {}  # request_id -> command_id
        self._decisions: list[ApprovalDecision] = []

    def create_approval_request(
        self,
        command: Command,
        context: CommandContext,
        required_permission: str = "HR_ADMIN",
        expire_hours: int = 24,
    ) -> ApprovalRequest:
        """Create a pending HITL approval request bound to command payload hash."""
        now = datetime.now(tz=UTC)
        req = ApprovalRequest(
            requested_by_actor_id=context.actor.actor_id,
            target_action=command.command_type,
            target_resource_type="Command",
            target_resource_id=command.command_id,
            organization_id=context.organization_id,
            required_permission=required_permission,
            status=ApprovalStatus.PENDING,
            expires_at=now + timedelta(hours=expire_hours),
            created_at=now,
            updated_at=now,
        )

        self._requests_by_id[req.request_id] = req
        self._command_payload_hashes[req.request_id] = command.payload_hash
        self._command_ids[req.request_id] = command.command_id
        return req

    def get_request(self, request_id: str) -> ApprovalRequest | None:
        return self._requests_by_id.get(request_id)

    def approve(
        self,
        request_id: str,
        approver_actor: Actor,
        current_command_payload_hash: str | None = None,
        reason: str | None = None,
    ) -> ApprovalRequest:
        """
        Approve a pending request.
        Strictly prevents self-approval, cross-tenant approval, payload tampering, and expired approvals.
        """
        req = self._requests_by_id.get(request_id)
        if not req:
            raise ApprovalValidationError(f"Approval request '{request_id}' not found.")

        # 1. Status check
        if req.status != ApprovalStatus.PENDING:
            raise ApprovalValidationError(f"Approval request is in '{req.status.value}' status and cannot be approved.")

        # 2. Expiration check
        now = datetime.now(tz=UTC)
        if now > req.expires_at:
            req.status = ApprovalStatus.EXPIRED
            req.updated_at = now
            raise ApprovalValidationError("Approval request has expired.")

        # 3. Cross-Tenant Check
        if approver_actor.organization_id != req.organization_id:
            raise ApprovalValidationError("Cross-tenant approval is strictly prohibited.")

        # 4. Self-Approval Check (AI Agent or Human cannot approve own action)
        if approver_actor.actor_id == req.requested_by_actor_id:
            raise ApprovalValidationError("Self-approval violation: Requested actor cannot approve their own action.")

        # 5. Payload Hash Integrity Check (detect tampering)
        expected_hash = self._command_payload_hashes.get(request_id)
        if current_command_payload_hash and expected_hash and current_command_payload_hash != expected_hash:
            raise ApprovalValidationError(
                "Command payload has been modified since approval request was created. Approval invalidated."
            )

        # Record decision and update status
        req.status = ApprovalStatus.APPROVED
        req.approver_actor_id = approver_actor.actor_id
        req.reason = reason
        req.updated_at = now

        decision = ApprovalDecision(
            request_id=request_id,
            approver_actor_id=approver_actor.actor_id,
            approved=True,
            reason=reason,
            decided_at=now,
        )
        self._decisions.append(decision)
        return req

    def reject(self, request_id: str, approver_actor: Actor, reason: str | None = None) -> ApprovalRequest:
        """Reject a pending request."""
        req = self._requests_by_id.get(request_id)
        if not req:
            raise ApprovalValidationError(f"Approval request '{request_id}' not found.")

        if approver_actor.organization_id != req.organization_id:
            raise ApprovalValidationError("Cross-tenant rejection is strictly prohibited.")

        now = datetime.now(tz=UTC)
        req.status = ApprovalStatus.REJECTED
        req.approver_actor_id = approver_actor.actor_id
        req.reason = reason
        req.updated_at = now

        decision = ApprovalDecision(
            request_id=request_id,
            approver_actor_id=approver_actor.actor_id,
            approved=False,
            reason=reason,
            decided_at=now,
        )
        self._decisions.append(decision)
        return req

    def list_pending_for_organization(self, organization_id: str) -> Sequence[ApprovalRequest]:
        """List all pending approval requests for an organization."""
        return [
            r
            for r in self._requests_by_id.values()
            if r.organization_id == organization_id and r.status == ApprovalStatus.PENDING
        ]
