"""
Specialized Agent Catalog — Central repository and introspection engine for all 24 AI HR agent blueprints.
"""

from __future__ import annotations

import logging

from backend.agents.specialized.domain.enums import SpecializedAgentRole, ToolAccessLevel
from backend.agents.specialized.domain.exceptions import (
    AgentSpecializationNotFoundError,
    InvalidSupervisorHierarchyError,
)
from backend.agents.specialized.domain.models import SpecializedAgentDefinition
from backend.agents.specialized.registry.definitions import SPECIALIZED_AGENT_DEFINITIONS

logger = logging.getLogger(__name__)


class SpecializedAgentCatalog:
    """
    Catalog of all standard specialized AI HR agents.
    Provides declarative inspection, supervisor hierarchy validation, and capability matrix queries.
    """

    _instance: SpecializedAgentCatalog | None = None

    def __init__(self) -> None:
        self._definitions: dict[SpecializedAgentRole, SpecializedAgentDefinition] = dict(SPECIALIZED_AGENT_DEFINITIONS)
        self._validate_supervisor_hierarchy()

    @classmethod
    def get_instance(cls) -> SpecializedAgentCatalog:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def list_definitions(self) -> list[SpecializedAgentDefinition]:
        """Return all 24 declarative agent definitions."""
        return list(self._definitions.values())

    def get_definition(self, role: SpecializedAgentRole | str) -> SpecializedAgentDefinition:
        """Resolve a specialized agent definition by role enum or string."""
        if isinstance(role, str):
            try:
                role = SpecializedAgentRole(role)
            except ValueError as err:
                raise AgentSpecializationNotFoundError(f"Specialized agent role [{role}] is not recognized in catalog.") from err

        if role not in self._definitions:
            raise AgentSpecializationNotFoundError(f"Specialized agent definition for [{role}] not found in catalog.")
        return self._definitions[role]

    def has_role(self, role: str) -> bool:
        """Check if role exists in catalog."""
        try:
            r = SpecializedAgentRole(role)
            return r in self._definitions
        except ValueError:
            return False

    def count(self) -> int:
        """Return total count of defined agents (must be 24)."""
        return len(self._definitions)

    def get_subordinates(self, supervisor_role: SpecializedAgentRole) -> list[SpecializedAgentDefinition]:
        """Return all agent definitions reporting directly to the given supervisor."""
        return [defn for defn in self._definitions.values() if defn.supervisor_role == supervisor_role]

    def get_supervisor_chain(self, role: SpecializedAgentRole) -> list[SpecializedAgentRole]:
        """
        Ascend the supervisor hierarchy from child to top-level supervisor.
        Returns list e.g. [RESUME_SCREENING_AGENT, RECRUITMENT_AGENT, HR_MANAGER_AGENT, EXECUTIVE_HR_AGENT]
        """
        chain: list[SpecializedAgentRole] = [role]
        curr_role: SpecializedAgentRole | None = role

        visited = {role}
        while curr_role is not None:
            defn = self.get_definition(curr_role)
            sup = defn.supervisor_role
            if sup is not None:
                if sup in visited:
                    raise InvalidSupervisorHierarchyError(f"Circular supervisor hierarchy detected at [{sup}]")
                visited.add(sup)
                chain.append(sup)
            curr_role = sup

        return chain

    def get_capability_matrix(self) -> dict[str, list[str]]:
        """Return a mapping of capability_token -> list of roles granted that capability."""
        matrix: dict[str, list[str]] = {}
        for role, defn in self._definitions.items():
            for cap in defn.capability_profile.capabilities:
                matrix.setdefault(cap, []).append(role.value)
        return matrix

    def get_tool_matrix(self) -> dict[str, dict[str, str]]:
        """Return a mapping of tool_id -> {role: access_level}."""
        matrix: dict[str, dict[str, str]] = {}
        for role, defn in self._definitions.items():
            for tool_id, access in defn.tool_policy.tool_access.items():
                matrix.setdefault(tool_id, {})[role.value] = access.value
        return matrix

    def is_tool_accessible(self, role: SpecializedAgentRole, tool_id: str) -> ToolAccessLevel:
        """Inspect if a tool is accessible for an agent without runtime execution."""
        defn = self.get_definition(role)
        return defn.tool_policy.get_access_level(tool_id)

    def _validate_supervisor_hierarchy(self) -> None:
        """Validate integrity of supervisor references across all 24 definitions."""
        for role, defn in self._definitions.items():
            if defn.supervisor_role is not None and defn.supervisor_role not in self._definitions:
                raise InvalidSupervisorHierarchyError(
                    f"Agent [{role}] references nonexistent supervisor [{defn.supervisor_role}]"
                )
            # Verify no circular dependencies
            self.get_supervisor_chain(role)
        logger.info("Successfully validated supervisor hierarchy across all specialized agents.")
