"""
Specialized Agent Bootstrap Service — Idempotent tenant initialization of the standard 24 AI HR agents.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

from backend.agents.application.agent_service import AgentService
from backend.agents.specialized.application.agent_factory import SpecializedAgentFactory
from backend.agents.specialized.domain.enums import SpecializedAgentRole
from backend.agents.specialized.domain.models import SpecializedAgentInstance
from backend.agents.specialized.registry.catalog import SpecializedAgentCatalog

logger = logging.getLogger(__name__)


class BootstrapResult(BaseModel):
    """Result of running specialized agent bootstrap for an organization."""

    organization_id: str
    total_expected: int = 24
    created_count: int = 0
    updated_count: int = 0
    skipped_count: int = 0
    instances: list[SpecializedAgentInstance] = Field(default_factory=list)


class SpecializedAgentBootstrap:
    """
    Idempotent bootstrap engine to initialize the 24 specialized AI HR agents per tenant organization.
    """

    def __init__(
        self,
        catalog: SpecializedAgentCatalog | None = None,
        factory: SpecializedAgentFactory | None = None,
        agent_service: AgentService | None = None,
    ) -> None:
        self.catalog = catalog or SpecializedAgentCatalog.get_instance()
        self.factory = factory or SpecializedAgentFactory(catalog=self.catalog)
        self.agent_service = agent_service or AgentService.get_instance()
        # In-memory store of specialized instances: org_id -> role -> instance
        self._instances: dict[str, dict[SpecializedAgentRole, SpecializedAgentInstance]] = {}

    def get_instances(self, organization_id: str) -> list[SpecializedAgentInstance]:
        """Return all instantiated specialized agents for an organization."""
        return list(self._instances.get(organization_id, {}).values())

    def get_instance_by_role(self, organization_id: str, role: SpecializedAgentRole | str) -> SpecializedAgentInstance | None:
        """Resolve a tenant's specialized agent instance by role."""
        if isinstance(role, str):
            try:
                role = SpecializedAgentRole(role)
            except ValueError:
                return None
        return self._instances.get(organization_id, {}).get(role)

    def bootstrap_organization(
        self,
        organization_id: str,
        roles: list[SpecializedAgentRole] | None = None,
        custom_parameters: dict[str, Any] | None = None,
    ) -> BootstrapResult:
        """
        Bootstrap the 24 standard agents for an organization idempotently.
        Running multiple times will NOT create duplicate agent records.
        """
        target_roles = roles or [defn.role for defn in self.catalog.list_definitions()]
        org_instances = self._instances.setdefault(organization_id, {})

        created = 0
        updated = 0
        skipped = 0
        result_instances: list[SpecializedAgentInstance] = []

        for role in target_roles:
            defn = self.catalog.get_definition(role)
            existing_instance = org_instances.get(role)

            if existing_instance is None:
                # 1. Create new agent
                agent, instance = self.factory.create_agent(
                    organization_id=organization_id,
                    role=role,
                    custom_parameters=custom_parameters,
                )
                # Register in core AgentService
                self.agent_service.register_agent(agent)
                org_instances[role] = instance
                result_instances.append(instance)
                created += 1
            else:
                # 2. Idempotent check: update version/metadata if changed
                if existing_instance.definition_version != defn.version:
                    existing_instance.definition_version = defn.version
                    existing_instance.autonomy_mode = defn.autonomy_mode
                    updated += 1
                else:
                    skipped += 1
                result_instances.append(existing_instance)

        logger.info(
            f"Bootstrapped [{len(target_roles)}] specialized agents for org [{organization_id}]: "
            f"created={created}, updated={updated}, skipped={skipped}"
        )

        return BootstrapResult(
            organization_id=organization_id,
            total_expected=len(target_roles),
            created_count=created,
            updated_count=updated,
            skipped_count=skipped,
            instances=result_instances,
        )
