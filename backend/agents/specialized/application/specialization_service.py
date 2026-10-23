"""
Specialized Agent Service — Central domain façade for specialized agent lifecycle, policy enforcement, and authority verification.
"""

from __future__ import annotations

import logging
from typing import Any

from backend.agents.memory.hierarchy.enums import MemoryTier
from backend.agents.specialized.application.agent_bootstrap import BootstrapResult, SpecializedAgentBootstrap
from backend.agents.specialized.domain.enums import SpecializedAgentRole, ToolAccessLevel
from backend.agents.specialized.domain.exceptions import (
    AgentPolicyViolationError,
    AgentSpecializationNotFoundError,
    ProhibitedToolExecutionError,
    UnauthorizedCapabilityError,
)
from backend.agents.specialized.domain.models import (
    CapabilityProfile,
    EvaluationContract,
    KnowledgePolicy,
    MemoryPolicy,
    SpecializedAgentDefinition,
    SpecializedAgentInstance,
    ToolPolicy,
)
from backend.agents.specialized.registry.catalog import SpecializedAgentCatalog
from backend.knowledge.domain.enums import AccessScopeType, KnowledgeClassification

logger = logging.getLogger(__name__)


class SpecializedAgentService:
    """
    Master application service for Specialized AI HR Agents.
    Enforces least-privilege capability boundaries, tool policies, memory scopes, and knowledge scoping.
    """

    _instance: SpecializedAgentService | None = None

    def __init__(
        self,
        catalog: SpecializedAgentCatalog | None = None,
        bootstrap: SpecializedAgentBootstrap | None = None,
    ) -> None:
        self.catalog = catalog or SpecializedAgentCatalog.get_instance()
        self.bootstrap = bootstrap or SpecializedAgentBootstrap(catalog=self.catalog)

    @classmethod
    def get_instance(cls) -> SpecializedAgentService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ── Catalog & Definitions ──────────────────────────────────────────────────

    def list_definitions(self) -> list[SpecializedAgentDefinition]:
        """Return all 24 declarative agent blueprints."""
        return self.catalog.list_definitions()

    def get_definition(self, role: SpecializedAgentRole | str) -> SpecializedAgentDefinition:
        """Resolve definition by role."""
        return self.catalog.get_definition(role)

    def get_capabilities(self, role: SpecializedAgentRole | str) -> CapabilityProfile:
        """Inspect capability profile for role."""
        return self.get_definition(role).capability_profile

    def get_tool_policy(self, role: SpecializedAgentRole | str) -> ToolPolicy:
        """Inspect tool policy for role."""
        return self.get_definition(role).tool_policy

    def get_knowledge_policy(self, role: SpecializedAgentRole | str) -> KnowledgePolicy:
        """Inspect knowledge policy for role."""
        return self.get_definition(role).knowledge_policy

    def get_memory_policy(self, role: SpecializedAgentRole | str) -> MemoryPolicy:
        """Inspect memory policy for role."""
        return self.get_definition(role).memory_policy

    def get_evaluation_contract(self, role: SpecializedAgentRole | str) -> EvaluationContract:
        """Inspect evaluation contract for role."""
        return self.get_definition(role).evaluation_contract

    # ── Tenant Instances & Bootstrap ──────────────────────────────────────────

    def bootstrap_tenant(self, organization_id: str, custom_parameters: dict[str, Any] | None = None) -> BootstrapResult:
        """Bootstrap the 24 standard agents for a tenant organization idempotently."""
        return self.bootstrap.bootstrap_organization(organization_id=organization_id, custom_parameters=custom_parameters)

    def list_tenant_instances(self, organization_id: str) -> list[SpecializedAgentInstance]:
        """List all active specialized agent instances for a tenant."""
        instances = self.bootstrap.get_instances(organization_id)
        if not instances:
            # Auto-bootstrap on first access
            self.bootstrap_tenant(organization_id)
            instances = self.bootstrap.get_instances(organization_id)
        return instances

    def get_tenant_instance(self, organization_id: str, role: SpecializedAgentRole | str) -> SpecializedAgentInstance:
        """Resolve tenant specialized agent instance."""
        instance = self.bootstrap.get_instance_by_role(organization_id, role)
        if not instance:
            # Auto-bootstrap and retry
            self.bootstrap_tenant(organization_id)
            instance = self.bootstrap.get_instance_by_role(organization_id, role)
            if not instance:
                raise AgentSpecializationNotFoundError(
                    f"Specialized agent [{role}] not found for organization [{organization_id}]."
                )
        return instance

    # ── Security & Policy Invariant Verifications ──────────────────────────────

    def verify_capability(self, role: SpecializedAgentRole | str, capability: str) -> None:
        """
        Verify that the agent possesses the capability and it is not prohibited.
        Raises UnauthorizedCapabilityError on failure.
        """
        defn = self.get_definition(role)
        if not defn.capability_profile.has_capability(capability):
            raise UnauthorizedCapabilityError(
                f"Agent [{defn.role.value}] is not authorized for capability [{capability}]. "
                f"Prohibited={defn.capability_profile.prohibited_capabilities}"
            )

    def verify_tool_access(self, role: SpecializedAgentRole | str, tool_id: str) -> ToolAccessLevel:
        """
        Verify tool access level.
        Raises ProhibitedToolExecutionError if tool is DENY or undeclared.
        """
        defn = self.get_definition(role)
        access = defn.tool_policy.get_access_level(tool_id)
        if access == ToolAccessLevel.DENY:
            raise ProhibitedToolExecutionError(f"Agent [{defn.role.value}] is prohibited from invoking tool [{tool_id}].")
        return access

    def verify_knowledge_access(
        self,
        role: SpecializedAgentRole | str,
        scope: AccessScopeType,
        classification: KnowledgeClassification,
    ) -> None:
        """
        Verify knowledge document scope and confidentiality tier.
        Raises AgentPolicyViolationError on failure.
        """
        defn = self.get_definition(role)
        k_pol = defn.knowledge_policy

        if scope in k_pol.prohibited_scopes or scope not in k_pol.allowed_scopes:
            raise AgentPolicyViolationError(
                f"Agent [{defn.role.value}] is prohibited from accessing knowledge scope [{scope.value}]."
            )

        # Classification hierarchy ranking
        class_rank = {
            KnowledgeClassification.PUBLIC: 0,
            KnowledgeClassification.INTERNAL: 1,
            KnowledgeClassification.CONFIDENTIAL: 2,
            KnowledgeClassification.SENSITIVE: 3,
            KnowledgeClassification.HIGHLY_SENSITIVE: 4,
            KnowledgeClassification.SYSTEM_ONLY: 5,
        }

        if class_rank.get(classification, 99) > class_rank.get(k_pol.max_classification, 0):
            raise AgentPolicyViolationError(
                f"Agent [{defn.role.value}] cannot access knowledge classification [{classification.value}] "
                f"(max allowed is [{k_pol.max_classification.value}])."
            )

    def verify_memory_tier_access(self, role: SpecializedAgentRole | str, tier: MemoryTier) -> None:
        """
        Verify memory hierarchy tier access.
        Raises AgentPolicyViolationError if tier is prohibited.
        """
        defn = self.get_definition(role)
        if not defn.memory_policy.is_tier_allowed(tier):
            raise AgentPolicyViolationError(f"Agent [{defn.role.value}] is prohibited from accessing memory tier [{tier.value}].")

    def validate_delegation(
        self, supervisor_role: SpecializedAgentRole | str, subordinate_role: SpecializedAgentRole | str
    ) -> None:
        """
        Verify that supervisor can delegate to subordinate, and subordinate cannot escalate privileges.
        """
        sup_defn = self.get_definition(supervisor_role)
        sub_defn = self.get_definition(subordinate_role)

        # Check supervisor hierarchy link
        chain = self.catalog.get_supervisor_chain(sub_defn.role)
        if sup_defn.role not in chain:
            raise AgentPolicyViolationError(
                f"Agent [{sup_defn.role.value}] is not in the supervisor hierarchy of [{sub_defn.role.value}]."
            )
