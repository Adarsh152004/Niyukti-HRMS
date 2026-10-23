"""
Agent Framework — Base Agent contract.

Defines the abstract BaseAgent, agent roles, statuses, capabilities,
and permission scopes. All HRMS agents must implement BaseAgent.

Agents communicate through the enterprise runtime — never directly
with each other or with external systems.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from backend.agents.autonomy import AutonomyLevel
from backend.governance.risk import RiskLevel


class AgentStatus(StrEnum):
    """Operational status of an HRMS agent."""

    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    SUSPENDED = "SUSPENDED"
    ERROR = "ERROR"
    MAINTENANCE = "MAINTENANCE"


@dataclass
class AgentCapability:
    """
    A discrete capability that an agent possesses.

    Capabilities are granted by the governance layer, not self-declared.
    """

    capability_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    action_types: list[str] = field(default_factory=list)
    resource_types: list[str] = field(default_factory=list)
    max_autonomy_level: AutonomyLevel = AutonomyLevel.LEVEL_2
    requires_approval_above_risk: RiskLevel = RiskLevel.MEDIUM


@dataclass
class AgentPermissionScope:
    """
    Scoped permissions for a specific agent.

    Permissions are explicitly defined — agents never receive
    unrestricted access. Any access outside this scope is denied.
    """

    agent_id: str
    agent_role: str
    readable_resources: list[str] = field(default_factory=list)
    writable_resources: list[str] = field(default_factory=list)
    executable_actions: list[str] = field(default_factory=list)
    forbidden_actions: list[str] = field(default_factory=list)
    can_access_pii: bool = False
    pii_accessible_fields: list[str] = field(default_factory=list)
    can_trigger_notifications: bool = False
    can_initiate_approvals: bool = True
    max_autonomy_level: AutonomyLevel = AutonomyLevel.LEVEL_2


class BaseAgent(ABC):
    """
    Abstract base class for all HRMS autonomous agents.

    Agents must:
    - Have a unique ID and declared role
    - Declare their capabilities and permission scope
    - Never bypass governance
    - Log all significant actions
    - Support pause/resume lifecycle control
    - Report performance metrics

    Agents must NOT:
    - Communicate directly with other agents (use EventBus)
    - Access resources outside their PermissionScope
    - Execute high-risk actions without HITL when required
    - Store or log raw PII
    """

    def __init__(
        self,
        agent_id: str | None = None,
        autonomy_level: AutonomyLevel = AutonomyLevel.LEVEL_2,
    ) -> None:
        self._agent_id: str = agent_id or str(uuid.uuid4())
        self._autonomy_level: AutonomyLevel = autonomy_level
        self._status: AgentStatus = AgentStatus.INACTIVE
        self._created_at: datetime = datetime.now(tz=UTC)

    # ── Identity ─────────────────────────────────────────────────────────────

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    @abstractmethod
    def role(self) -> str:
        """The declared agent role (must match HRAgentRole enum value)."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of this agent's purpose."""
        ...

    # ── Autonomy & Status ────────────────────────────────────────────────────

    @property
    def autonomy_level(self) -> AutonomyLevel:
        return self._autonomy_level

    @autonomy_level.setter
    def autonomy_level(self, level: AutonomyLevel) -> None:
        self._autonomy_level = level

    @property
    def status(self) -> AgentStatus:
        return self._status

    # ── Capabilities & Permissions ───────────────────────────────────────────

    @property
    @abstractmethod
    def capabilities(self) -> list[AgentCapability]:
        """Declared capabilities of this agent."""
        ...

    @property
    @abstractmethod
    def permission_scope(self) -> AgentPermissionScope:
        """Scoped permissions for this agent instance."""
        ...

    # ── Lifecycle ────────────────────────────────────────────────────────────

    async def start(self) -> None:
        """Activate the agent. Subclasses may override for initialization."""
        self._status = AgentStatus.ACTIVE

    async def pause(self) -> None:
        """Pause the agent. It will not accept new tasks until resumed."""
        self._status = AgentStatus.PAUSED

    async def resume(self) -> None:
        """Resume a paused agent."""
        if self._status == AgentStatus.PAUSED:
            self._status = AgentStatus.ACTIVE

    async def suspend(self, reason: str = "") -> None:
        """Suspend the agent (requires admin action to restore)."""
        self._status = AgentStatus.SUSPENDED

    async def stop(self) -> None:
        """Stop and deactivate the agent."""
        self._status = AgentStatus.INACTIVE

    # ── Execution ────────────────────────────────────────────────────────────

    @abstractmethod
    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a task payload and return the result.

        Subclasses MUST check governance constraints before executing.
        Subclasses MUST never log raw PII.
        """
        ...

    # ── Introspection ────────────────────────────────────────────────────────

    def info(self) -> dict[str, Any]:
        """Return a non-PII summary of the agent's current state."""
        return {
            "agent_id": self._agent_id,
            "role": self.role,
            "description": self.description,
            "status": self._status.value,
            "autonomy_level": self._autonomy_level.value,
            "autonomy_label": self._autonomy_level.label,
            "created_at": self._created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._agent_id!r}, role={self.role!r}, status={self._status})"
