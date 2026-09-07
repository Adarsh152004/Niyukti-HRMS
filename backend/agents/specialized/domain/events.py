"""
Specialized Agent Domain Events — Emitted during specialized agent registration, configuration, capability binding, policy binding, and activation.
"""

from __future__ import annotations

from backend.runtime.events import Event


class SpecializedAgentRegistered(Event):
    """Emitted when a specialized agent definition is registered or updated in the catalog."""

    def __init__(
        self,
        role: str,
        display_name: str,
        version: str,
        autonomy_mode: str,
        correlation_id: str | None = None,
    ) -> None:
        super().__init__(
            event_type="specialized_agent.registered",
            source="specialized_agent_catalog",
            payload={
                "role": role,
                "display_name": display_name,
                "version": version,
                "autonomy_mode": autonomy_mode,
            },
            correlation_id=correlation_id,
        )


class SpecializedAgentConfigured(Event):
    """Emitted when a specialized agent instance is configured for a tenant."""

    def __init__(
        self,
        instance_id: str,
        organization_id: str,
        role: str,
        agent_id: str,
        actor_id: str,
        correlation_id: str | None = None,
    ) -> None:
        super().__init__(
            event_type="specialized_agent.configured",
            source="specialized_agent_factory",
            payload={
                "instance_id": instance_id,
                "organization_id": organization_id,
                "role": role,
                "agent_id": agent_id,
                "actor_id": actor_id,
            },
            correlation_id=correlation_id,
        )


class SpecializedAgentCapabilityBound(Event):
    """Emitted when capability profiles are bound to an agent."""

    def __init__(
        self,
        agent_id: str,
        organization_id: str,
        role: str,
        capabilities_count: int,
        prohibited_count: int,
        correlation_id: str | None = None,
    ) -> None:
        super().__init__(
            event_type="specialized_agent.capability_bound",
            source="specialized_agent_factory",
            payload={
                "agent_id": agent_id,
                "organization_id": organization_id,
                "role": role,
                "capabilities_count": capabilities_count,
                "prohibited_count": prohibited_count,
            },
            correlation_id=correlation_id,
        )


class SpecializedAgentToolBound(Event):
    """Emitted when tool policies are bound to an agent."""

    def __init__(
        self,
        agent_id: str,
        organization_id: str,
        role: str,
        allowed_tools_count: int,
        approval_tools_count: int,
        correlation_id: str | None = None,
    ) -> None:
        super().__init__(
            event_type="specialized_agent.tool_bound",
            source="specialized_agent_factory",
            payload={
                "agent_id": agent_id,
                "organization_id": organization_id,
                "role": role,
                "allowed_tools_count": allowed_tools_count,
                "approval_tools_count": approval_tools_count,
            },
            correlation_id=correlation_id,
        )


class SpecializedAgentPolicyBound(Event):
    """Emitted when knowledge, memory, SLA, and evaluation policies are bound to an agent."""

    def __init__(
        self,
        agent_id: str,
        organization_id: str,
        role: str,
        policy_types: list[str],
        correlation_id: str | None = None,
    ) -> None:
        super().__init__(
            event_type="specialized_agent.policy_bound",
            source="specialized_agent_factory",
            payload={
                "agent_id": agent_id,
                "organization_id": organization_id,
                "role": role,
                "policy_types": policy_types,
            },
            correlation_id=correlation_id,
        )


class SpecializedAgentActivated(Event):
    """Emitted when a specialized agent instance is activated in a tenant organization."""

    def __init__(
        self,
        agent_id: str,
        organization_id: str,
        role: str,
        correlation_id: str | None = None,
    ) -> None:
        super().__init__(
            event_type="specialized_agent.activated",
            source="specialized_agent_service",
            payload={
                "agent_id": agent_id,
                "organization_id": organization_id,
                "role": role,
            },
            correlation_id=correlation_id,
        )


class SpecializedAgentVersionChanged(Event):
    """Emitted when an agent's definition version is upgraded."""

    def __init__(
        self,
        agent_id: str,
        organization_id: str,
        role: str,
        old_version: str,
        new_version: str,
        correlation_id: str | None = None,
    ) -> None:
        super().__init__(
            event_type="specialized_agent.version_changed",
            source="specialized_agent_service",
            payload={
                "agent_id": agent_id,
                "organization_id": organization_id,
                "role": role,
                "old_version": old_version,
                "new_version": new_version,
            },
            correlation_id=correlation_id,
        )
