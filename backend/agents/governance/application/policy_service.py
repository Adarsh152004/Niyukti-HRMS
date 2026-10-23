"""
Governance Policy Service — Evaluates agent actions against tenant operating policies.
Determines GovernanceDecision (ALLOW, WARN, REQUIRE_APPROVAL, THROTTLE, PAUSE, SUSPEND, DENY).
Governance policies can NEVER grant permissions or bypass Authorization.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from backend.agents.governance.domain.enums import GovernanceDecision, GovernanceState, ViolationType
from backend.agents.governance.domain.exceptions import AgentQuarantinedError, GovernanceAccessDeniedError
from backend.agents.governance.domain.models import AgentGovernancePolicy, GovernanceViolation
from backend.agents.governance.infrastructure.database.repositories import InMemoryGovernanceRepository
from backend.agents.governance.ports.repositories import GovernanceRepositoryPort
from backend.hrms.domain.actor import Actor, ActorType
from backend.runtime.events import Event, EventBus

logger = logging.getLogger(__name__)


class GovernancePolicyService:
    """
    Evaluates agent behavior against tenant governance policies.
    """

    def __init__(
        self,
        repository: GovernanceRepositoryPort | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.repository = repository or InMemoryGovernanceRepository()
        self.event_bus = event_bus or EventBus.get_instance()

    async def get_or_create_policy(self, organization_id: str, agent_id: str) -> AgentGovernancePolicy:
        """Retrieve policy for agent or initialize tenant default."""
        policy = await self.repository.get_policy(organization_id, agent_id)
        if not policy:
            policy = AgentGovernancePolicy(
                organization_id=organization_id,
                agent_id=agent_id,
            )
            await self.repository.save_policy(policy)
        return policy

    async def update_policy(
        self,
        organization_id: str,
        agent_id: str,
        actor: Actor,
        name: str | None = None,
        description: str | None = None,
        max_reasoning_steps: int | None = None,
        max_tool_calls: int | None = None,
        max_delegation_depth: int | None = None,
        auto_quarantine: bool | None = None,
        governance_state: GovernanceState | None = None,
    ) -> AgentGovernancePolicy:
        """
        Update governance policy.
        SECURITY INVARIANT: Approver MUST be HUMAN/System. AI Agents CANNOT update policies!
        """
        if actor.actor_type == ActorType.AI_AGENT:
            raise GovernanceAccessDeniedError("AI Agents are strictly prohibited from modifying governance policies.")

        if actor.organization_id != organization_id:
            raise GovernanceAccessDeniedError("Actor organization mismatch.")

        policy = await self.get_or_create_policy(organization_id, agent_id)

        if name is not None:
            policy.name = name
        if description is not None:
            policy.description = description
        if max_reasoning_steps is not None:
            policy.max_reasoning_steps_per_task = max_reasoning_steps
        if max_tool_calls is not None:
            policy.max_tool_calls_per_task = max_tool_calls
        if max_delegation_depth is not None:
            policy.max_delegation_depth = max_delegation_depth
        if auto_quarantine is not None:
            policy.auto_quarantine_on_violation = auto_quarantine
        if governance_state is not None:
            policy.governance_state = governance_state

        saved = await self.repository.save_policy(policy)

        await self.event_bus.publish(
            Event(
                event_type="hrms.agent.governance.policy_created",
                source="governance_policy_service",
                payload={
                    "agent_id": agent_id,
                    "organization_id": organization_id,
                    "actor_id": actor.actor_id,
                    "governance_state": saved.governance_state.value,
                },
            )
        )

        return saved

    async def evaluate_execution_policy(
        self,
        organization_id: str,
        agent_id: str,
        tool_name: str | None = None,
        command_name: str | None = None,
        delegation_depth: int = 0,
        risk_level: str = "LOW",
    ) -> GovernanceDecision:
        """
        Evaluate proposed action against governance policies and return GovernanceDecision.
        """
        policy = await self.get_or_create_policy(organization_id, agent_id)

        # 1. State check
        if policy.governance_state in [GovernanceState.QUARANTINED, GovernanceState.DISABLED]:
            raise AgentQuarantinedError(
                f"Agent '{agent_id}' is in {policy.governance_state.value} state and cannot execute actions."
            )

        if policy.governance_state == GovernanceState.RESTRICTED:
            return GovernanceDecision.REQUIRE_APPROVAL

        # 2. Delegation depth check
        if delegation_depth > policy.max_delegation_depth:
            await self.record_violation(
                organization_id,
                agent_id,
                ViolationType.RATE_LIMIT_EXCEEDED,
                f"Delegation depth {delegation_depth} exceeds maximum limit {policy.max_delegation_depth}.",
            )
            return GovernanceDecision.DENY

        # 3. Prohibited tool check
        if tool_name and policy.prohibited_tool_categories:
            for category in policy.prohibited_tool_categories:
                if category.lower() in tool_name.lower():
                    await self.record_violation(
                        organization_id,
                        agent_id,
                        ViolationType.UNAUTHORIZED_TOOL_ATTEMPT,
                        f"Tool '{tool_name}' belongs to prohibited category '{category}'.",
                    )
                    return GovernanceDecision.DENY

        # 4. Mandatory approval for high risk
        if risk_level in ["HIGH", "CRITICAL"]:
            return GovernanceDecision.REQUIRE_APPROVAL

        return GovernanceDecision.ALLOW

    async def validate_agent_execution(self, organization_id: str, agent_id: str) -> None:
        """Validate agent execution status."""
        policy = await self.get_or_create_policy(organization_id, agent_id)
        if policy.governance_state in [GovernanceState.QUARANTINED, GovernanceState.DISABLED]:
            raise AgentQuarantinedError(
                f"Agent '{agent_id}' is in {policy.governance_state.value} state and cannot execute actions."
            )

    async def record_violation(
        self,
        organization_id: str,
        agent_id: str,
        violation_type: ViolationType | str,
        details: str,
        task_id: str | None = None,
    ) -> GovernanceViolation:
        """Record a governance policy violation and quarantine agent if configured."""
        # Ensure violation_type is Enum
        if isinstance(violation_type, str):
            try:
                from backend.agents.governance.domain.enums import ViolationType as VType

                violation_type = VType(violation_type)
            except ValueError:
                pass

        violation = GovernanceViolation(
            organization_id=organization_id,
            agent_id=agent_id,
            task_id=task_id,
            violation_type=violation_type if not isinstance(violation_type, str) else ViolationType.POLICY_BYPASS_ATTEMPT,
            details=details,
        )
        saved = await self.repository.save_violation(violation)

        policy = await self.get_or_create_policy(organization_id, agent_id)
        # Quarantine only on POLICY_BYPASS_ATTEMPT
        if (
            policy.auto_quarantine_on_violation
            and violation_type == ViolationType.POLICY_BYPASS_ATTEMPT
            and policy.governance_state != GovernanceState.QUARANTINED
        ):
            policy.governance_state = GovernanceState.QUARANTINED
            violation.action_taken = "QUARANTINED"
            await self.repository.save_policy(policy)
            logger.warning(f"Agent '{agent_id}' QUARANTINED due to violation: {details}")

            await self.event_bus.publish(
                Event(
                    event_type="hrms.agent.policy_violation_detected",
                    source="governance_policy_service",
                    payload={
                        "agent_id": agent_id,
                        "organization_id": organization_id,
                        "violation_type": violation_type.value if hasattr(violation_type, "value") else str(violation_type),
                        "details": details,
                    },
                )
            )

        return saved

    async def list_violations(self, organization_id: str, agent_id: str) -> Sequence[GovernanceViolation]:
        """List violations recorded for an agent."""
        return await self.repository.list_violations(organization_id, agent_id)
