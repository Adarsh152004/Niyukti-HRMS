"""
Knowledge Access Service — Enforces strict pre-retrieval authorization.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from backend.knowledge.domain.enums import AccessScopeType, KnowledgeClassification
from backend.knowledge.domain.models import KnowledgeDocument
from backend.knowledge.ports.repositories import KnowledgeAccessPolicyRepositoryPort

logger = logging.getLogger(__name__)

# Classification hierarchy for role access
CLASSIFICATION_HIERARCHY: dict[KnowledgeClassification, int] = {
    KnowledgeClassification.PUBLIC: 0,
    KnowledgeClassification.INTERNAL: 1,
    KnowledgeClassification.CONFIDENTIAL: 2,
    KnowledgeClassification.EMPLOYEE_PRIVATE: 3,
    KnowledgeClassification.SENSITIVE: 4,
    KnowledgeClassification.HR_ONLY: 5,
    KnowledgeClassification.MANAGER_ONLY: 5,
    KnowledgeClassification.EXECUTIVE_ONLY: 6,
    KnowledgeClassification.HIGHLY_SENSITIVE: 7,
    KnowledgeClassification.SYSTEM_ONLY: 8,
}


class KnowledgeAccessService:
    """Pre-retrieval authorization service validating actor and agent access scopes."""

    def __init__(self, policy_repo: KnowledgeAccessPolicyRepositoryPort) -> None:
        self.policy_repo = policy_repo

    async def is_actor_authorized_for_document(
        self,
        document: KnowledgeDocument,
        actor_id: str,
        actor_roles: Sequence[str],
        actor_department_id: str | None = None,
        agent_id: str | None = None,
        agent_capabilities: Sequence[str] | None = None,
    ) -> bool:
        """
        Evaluate if an actor or AI agent is legally authorized to retrieve content from document.
        The LLM is NEVER the authority.
        """
        # Super Admin bypasses scope check within tenant boundary
        if "SUPER_ADMIN" in actor_roles or "ADMIN" in actor_roles:
            return True

        # System Only documents are restricted
        if document.classification == KnowledgeClassification.SYSTEM_ONLY and "SYSTEM" not in actor_roles:
            return False

        # Executive Only documents
        if document.classification == KnowledgeClassification.EXECUTIVE_ONLY and not any(
            r in actor_roles for r in ["EXECUTIVE", "CEO", "CHRO"]
        ):
            return False

        # HR Only documents
        if (
            document.classification == KnowledgeClassification.HR_ONLY
            and not any(r in actor_roles for r in ["HR_ADMIN", "HR_MANAGER", "CHRO", "RECRUITER", "PAYROLL_ADMIN"])
            and not (agent_capabilities and any("hr:" in c for c in agent_capabilities))
        ):
            return False

        # Manager Only documents
        if document.classification == KnowledgeClassification.MANAGER_ONLY and not any(
            r in actor_roles for r in ["MANAGER", "HR_MANAGER", "EXECUTIVE", "CEO", "CHRO"]
        ):
            return False

        # Fetch custom policy if registered
        policy = await self.policy_repo.get_policy(document.organization_id, document.document_id)
        if not policy:
            # Default open for PUBLIC and INTERNAL to organization members
            return document.classification in [
                KnowledgeClassification.PUBLIC,
                KnowledgeClassification.INTERNAL,
            ]

        # Scope Type Evaluation
        if policy.scope_type == AccessScopeType.ALL_EMPLOYEES:
            return True
        elif policy.scope_type == AccessScopeType.DEPARTMENT_ONLY:
            return bool(actor_department_id and actor_department_id in policy.allowed_departments)
        elif policy.scope_type == AccessScopeType.ROLE_BASED:
            return any(r in policy.allowed_roles for r in actor_roles)
        elif policy.scope_type == AccessScopeType.INDIVIDUAL_EMPLOYEE:
            return bool(actor_id in policy.allowed_employee_ids or document.owner_id == actor_id)
        elif policy.scope_type == AccessScopeType.AGENT_CAPABILITY:
            return bool(agent_capabilities and any(cap in policy.allowed_capabilities for cap in agent_capabilities))

        return False

    async def filter_accessible_documents(
        self,
        documents: Sequence[KnowledgeDocument],
        actor_id: str,
        actor_roles: Sequence[str],
        actor_department_id: str | None = None,
        agent_id: str | None = None,
        agent_capabilities: Sequence[str] | None = None,
    ) -> list[KnowledgeDocument]:
        """Pre-filter candidate documents to strictly authorized set."""
        authorized: list[KnowledgeDocument] = []
        for doc in documents:
            if await self.is_actor_authorized_for_document(
                document=doc,
                actor_id=actor_id,
                actor_roles=actor_roles,
                actor_department_id=actor_department_id,
                agent_id=agent_id,
                agent_capabilities=agent_capabilities,
            ):
                authorized.append(doc)
        return authorized
