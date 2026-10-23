"""
Specialized Agent Factory — Creates fully-configured runtime Agent entities from declarative definitions.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from backend.agents.domain.enums import AgentStatus, AgentType
from backend.agents.domain.models import Agent, AgentCapability
from backend.agents.sandbox.sla import AgentSLAContract, SLAManager
from backend.agents.specialized.domain.enums import SpecializedAgentRole
from backend.agents.specialized.domain.events import (
    SpecializedAgentCapabilityBound,
    SpecializedAgentConfigured,
    SpecializedAgentPolicyBound,
    SpecializedAgentToolBound,
)
from backend.agents.specialized.domain.models import (
    SpecializedAgentInstance,
)
from backend.agents.specialized.registry.catalog import SpecializedAgentCatalog
from backend.runtime.events import EventBus

logger = logging.getLogger(__name__)


class SpecializedAgentFactory:
    """
    Factory creating runtime Agent instances bound to tenant Organizations from declarative blueprints.
    """

    def __init__(
        self,
        catalog: SpecializedAgentCatalog | None = None,
        event_bus: EventBus | None = None,
        sla_manager: SLAManager | None = None,
    ) -> None:
        self.catalog = catalog or SpecializedAgentCatalog.get_instance()
        self.event_bus = event_bus or EventBus.get_instance()
        self.sla_manager = sla_manager or SLAManager.get_instance()
        self._background_tasks: set[Any] = set()

    def create_agent(
        self,
        organization_id: str,
        role: SpecializedAgentRole | str,
        actor_id: str | None = None,
        custom_parameters: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> tuple[Agent, SpecializedAgentInstance]:
        """
        Instantiate a specialized Agent domain model and its corresponding SpecializedAgentInstance.
        """
        defn = self.catalog.get_definition(role)
        role_enum = defn.role

        resolved_actor_id = actor_id or f"actor-ai-{role_enum.value.lower()}-{organization_id}"
        agent_id = f"agent-{role_enum.value.lower()}-{uuid.uuid4().hex[:8]}"

        # 1. Build Agent Capabilities
        domain_capabilities: list[AgentCapability] = []
        for cap_token in defn.capability_profile.capabilities:
            domain_capabilities.append(
                AgentCapability(
                    capability_id=f"cap_{cap_token.replace(':', '_')}",
                    name=cap_token,
                    resource=cap_token.split(":")[0] if ":" in cap_token else "general",
                    actions=[cap_token.split(":")[1]] if ":" in cap_token else ["execute"],
                    risk_level="HIGH" if "terminate" in cap_token or "salary" in cap_token else "MEDIUM",
                    requires_hitl=defn.autonomy_mode.value in ["ASSISTED", "SUPERVISED"],
                    enabled=True,
                )
            )

        # 2. Instantiate Core Agent Domain Model
        agent = Agent(
            agent_id=agent_id,
            organization_id=organization_id,
            name=f"{role_enum.value.lower()}-{organization_id}",
            display_name=defn.display_name,
            description=defn.purpose,
            agent_type=AgentType.HR_AGENT,
            status=AgentStatus.ACTIVE if defn.is_active else AgentStatus.CREATED,
            actor_id=resolved_actor_id,
            version=1,
            capabilities=domain_capabilities,
            max_concurrent_tasks=5,
            metadata={
                "specialized_role": role_enum.value,
                "definition_version": defn.version,
                "autonomy_mode": defn.autonomy_mode.value,
                "supervisor_role": defn.supervisor_role.value if defn.supervisor_role else None,
                "daily_budget_usd": defn.daily_budget_usd,
                "custom_parameters": custom_parameters or {},
            },
        )

        # 3. Instantiate Specialized Agent Instance Record
        instance = SpecializedAgentInstance(
            organization_id=organization_id,
            role=role_enum,
            agent_id=agent_id,
            actor_id=resolved_actor_id,
            definition_version=defn.version,
            autonomy_mode=defn.autonomy_mode,
            is_enabled=defn.is_active,
            custom_parameters=custom_parameters or {},
        )

        # 4. Bind SLA Contract
        sla = AgentSLAContract(
            agent_id=agent_id,
            organization_id=organization_id,
            max_execution_time_seconds=defn.max_execution_time_seconds,
            max_cost_per_task_usd=round(defn.daily_budget_usd / 20.0, 2),
            max_tool_calls_per_task=defn.max_tool_calls_per_task,
            max_delegation_depth=defn.max_delegation_depth,
            min_evaluation_score=defn.evaluation_contract.min_accuracy_score,
        )
        self.sla_manager.register_sla(sla)

        # 5. Emit Domain Events
        self._publish_event(
            SpecializedAgentConfigured(
                instance_id=instance.instance_id,
                organization_id=organization_id,
                role=role_enum.value,
                agent_id=agent_id,
                actor_id=resolved_actor_id,
                correlation_id=correlation_id,
            )
        )
        self._publish_event(
            SpecializedAgentCapabilityBound(
                agent_id=agent_id,
                organization_id=organization_id,
                role=role_enum.value,
                capabilities_count=len(defn.capability_profile.capabilities),
                prohibited_count=len(defn.capability_profile.prohibited_capabilities),
                correlation_id=correlation_id,
            )
        )
        allowed_count = sum(1 for a in defn.tool_policy.tool_access.values() if a.value == "ALLOW")
        approval_count = sum(1 for a in defn.tool_policy.tool_access.values() if a.value == "REQUIRES_APPROVAL")
        self._publish_event(
            SpecializedAgentToolBound(
                agent_id=agent_id,
                organization_id=organization_id,
                role=role_enum.value,
                allowed_tools_count=allowed_count,
                approval_tools_count=approval_count,
                correlation_id=correlation_id,
            )
        )
        self._publish_event(
            SpecializedAgentPolicyBound(
                agent_id=agent_id,
                organization_id=organization_id,
                role=role_enum.value,
                policy_types=["KNOWLEDGE", "MEMORY", "SLA", "EVALUATION", "MODEL"],
                correlation_id=correlation_id,
            )
        )

        logger.info(f"Instantiated specialized agent [{role_enum.value}] with id [{agent_id}] for org [{organization_id}]")
        return agent, instance

    def _publish_event(self, event: Any) -> None:
        """Safely schedule event publication on running event loop or synchronous fallback."""
        try:
            import asyncio

            try:
                loop = asyncio.get_running_loop()
                task = loop.create_task(self.event_bus.publish(event))
                self._background_tasks.add(task)
                task.add_done_callback(self._background_tasks.discard)
            except RuntimeError:
                asyncio.run(self.event_bus.publish(event))
        except Exception as e:
            logger.debug(f"Event emission deferred: {e}")
