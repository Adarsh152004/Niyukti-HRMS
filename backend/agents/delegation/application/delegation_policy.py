"""
Delegation Policy — Strict policy enforcement for Multi-Agent Delegation.
Enforces capability intersection, tenant isolation, agent active status, and privilege escalation prevention.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from backend.agents.delegation.domain.exceptions import (
    DelegationAccessDeniedError,
    DelegationValidationError,
    PrivilegeEscalationError,
    RecursiveDelegationDeniedError,
)
from backend.agents.delegation.domain.models import Delegation
from backend.agents.domain.enums import AgentStatus
from backend.agents.domain.models import Agent, AgentCapability

logger = logging.getLogger(__name__)

MAX_DELEGATION_TTL_HOURS = 24


class DelegationPolicy:
    """
    Evaluates delegation requests against strict security and governance invariants.
    """

    def validate_delegation(
        self,
        delegator: Agent,
        delegate: Agent,
        requested_capabilities: list[AgentCapability],
        organization_id: str,
        expires_at: datetime,
        parent_delegation: Delegation | None = None,
    ) -> list[AgentCapability]:
        """
        Validate delegation request and compute effective worker capability subset.
        Returns the computed effective worker capabilities.
        Raises DelegationValidationError / PrivilegeEscalationError if unsafe.
        """
        # 1. Active Agent Checks
        if delegator.status != AgentStatus.ACTIVE:
            raise DelegationAccessDeniedError(
                f"Delegator agent '{delegator.agent_id}' is not ACTIVE (status: {delegator.status})."
            )

        if delegate.status != AgentStatus.ACTIVE:
            raise DelegationAccessDeniedError(
                f"Delegate worker agent '{delegate.agent_id}' is not ACTIVE (status: {delegate.status})."
            )

        # 2. Strict Tenant Matching
        if delegator.organization_id != organization_id:
            raise DelegationAccessDeniedError(
                f"Delegator organization '{delegator.organization_id}' mismatch with tenant '{organization_id}'."
            )

        if delegate.organization_id != organization_id:
            raise DelegationAccessDeniedError(
                f"Delegate worker organization '{delegate.organization_id}' mismatch with tenant '{organization_id}'."
            )

        # 3. Expiration Check
        now = datetime.now(tz=UTC)
        if expires_at <= now:
            raise DelegationValidationError("Delegation expiration timestamp must be in the future.")

        max_expires = now + timedelta(hours=MAX_DELEGATION_TTL_HOURS)
        if expires_at > max_expires:
            raise DelegationValidationError(
                f"Delegation expiration cannot exceed maximum allowed duration ({MAX_DELEGATION_TTL_HOURS} hours)."
            )

        # 4. Recursive Delegation Policy Check
        if parent_delegation:
            if not parent_delegation.allow_further_delegation:
                raise RecursiveDelegationDeniedError(
                    f"Parent delegation '{parent_delegation.delegation_id}' explicitly forbids recursive delegation."
                )
            if parent_delegation.organization_id != organization_id:
                raise DelegationAccessDeniedError("Parent delegation tenant mismatch.")

        # 5. Capability Intersection Check & Privilege Escalation Prevention
        effective_capabilities: list[AgentCapability] = []

        for req_cap in requested_capabilities:
            # Delegator must possess an enabled capability covering resource & requested actions
            matching_delegator_cap = self._find_matching_capability(delegator.capabilities, req_cap)

            if not matching_delegator_cap:
                raise PrivilegeEscalationError(
                    f"Delegator '{delegator.name}' does not possess capability for resource '{req_cap.resource}' "
                    f"with actions {req_cap.actions}."
                )

            # Check if requested actions exceed delegator actions
            delegator_actions = set(matching_delegator_cap.actions)
            requested_actions = set(req_cap.actions)

            if not requested_actions.issubset(delegator_actions):
                unauthorized_actions = requested_actions - delegator_actions
                raise PrivilegeEscalationError(
                    f"Delegation attempts privilege escalation. Delegator lacks actions {list(unauthorized_actions)} "
                    f"for resource '{req_cap.resource}'."
                )

            # If parent delegation exists, also verify against parent capabilities
            if parent_delegation:
                matching_parent_cap = self._find_matching_capability(parent_delegation.capabilities, req_cap)
                if not matching_parent_cap:
                    raise PrivilegeEscalationError(
                        f"Recursive delegation exceeds parent delegation capabilities for resource '{req_cap.resource}'."
                    )

            # Build sanitized effective worker capability
            effective_cap = AgentCapability(
                capability_id=f"cap-del-{req_cap.resource}-{'-'.join(req_cap.actions)}",
                name=f"Delegated {req_cap.name}",
                description=req_cap.description or f"Delegated capability from {delegator.agent_id}",
                resource=req_cap.resource,
                actions=list(req_cap.actions),
                risk_level=matching_delegator_cap.risk_level,
                requires_hitl=matching_delegator_cap.requires_hitl or req_cap.requires_hitl,
                enabled=True,
            )
            effective_capabilities.append(effective_cap)

        return effective_capabilities

    def _find_matching_capability(
        self,
        capabilities: list[AgentCapability],
        target: AgentCapability,
    ) -> AgentCapability | None:
        """Find an enabled capability matching target resource."""
        for cap in capabilities:
            if cap.enabled and cap.resource == target.resource:
                return cap
        return None
