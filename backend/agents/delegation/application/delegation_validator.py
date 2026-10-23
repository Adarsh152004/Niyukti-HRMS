"""
Delegation Validator — Pre-flight validator for multi-agent delegation operations.
"""

from __future__ import annotations

import logging
from datetime import datetime

from backend.agents.application.agent_service import AgentService
from backend.agents.delegation.application.delegation_policy import DelegationPolicy
from backend.agents.delegation.domain.models import Delegation
from backend.agents.domain.models import AgentCapability

logger = logging.getLogger(__name__)


class DelegationValidator:
    """
    Validates delegation requests by combining registry lookups with DelegationPolicy checks.
    """

    def __init__(
        self,
        agent_service: AgentService | None = None,
        policy: DelegationPolicy | None = None,
    ) -> None:
        self.agent_service = agent_service or AgentService()
        self.policy = policy or DelegationPolicy()

    async def validate_request(
        self,
        organization_id: str,
        delegator_agent_id: str,
        delegate_agent_id: str,
        requested_capabilities: list[AgentCapability],
        expires_at: datetime,
        parent_delegation: Delegation | None = None,
    ) -> list[AgentCapability]:
        """
        Fetch delegator & delegate from AgentRegistry and validate via DelegationPolicy.
        Returns the computed effective capabilities.
        """
        from backend.agents.delegation.domain.exceptions import DelegationAccessDeniedError

        try:
            delegator = await self.agent_service.get_agent(organization_id, delegator_agent_id)
        except Exception as e:
            raise DelegationAccessDeniedError(f"Delegator agent '{delegator_agent_id}' validation failed: {e}") from e

        if not delegator:
            raise DelegationAccessDeniedError(
                f"Delegator agent '{delegator_agent_id}' not found in organization '{organization_id}'."
            )

        try:
            delegate = await self.agent_service.get_agent(organization_id, delegate_agent_id)
        except Exception as e:
            raise DelegationAccessDeniedError(f"Delegate worker agent '{delegate_agent_id}' validation failed: {e}") from e

        if not delegate:
            raise DelegationAccessDeniedError(
                f"Delegate worker agent '{delegate_agent_id}' not found in organization '{organization_id}'."
            )

        return self.policy.validate_delegation(
            delegator=delegator,
            delegate=delegate,
            requested_capabilities=requested_capabilities,
            organization_id=organization_id,
            expires_at=expires_at,
            parent_delegation=parent_delegation,
        )
