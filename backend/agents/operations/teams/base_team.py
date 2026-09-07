"""
Base Multi-Agent Team — Supervisor-worker coordination pattern with task decomposition and consensus aggregation.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from backend.agents.operations.governance.collusion_detector import CollusionDetector
from backend.agents.operations.messaging.bus import AgentMessageBus
from backend.agents.operations.messaging.models import AgentMessage, AgentMessageType
from backend.agents.specialized.domain.enums import SpecializedAgentRole

logger = logging.getLogger(__name__)


class MultiAgentTeam(ABC):
    """
    Abstract Base Class for Multi-Agent Business Teams.
    """

    def __init__(
        self,
        organization_id: str,
        supervisor_role: SpecializedAgentRole,
        worker_roles: list[SpecializedAgentRole],
        bus: AgentMessageBus | None = None,
        collusion_detector: CollusionDetector | None = None,
    ) -> None:
        self.organization_id = organization_id
        self.supervisor_role = supervisor_role
        self.worker_roles = worker_roles
        self.bus = bus or AgentMessageBus.get_instance()
        self.detector = collusion_detector or CollusionDetector.get_instance()

    async def delegate_task_to_worker(
        self,
        worker_role: SpecializedAgentRole,
        task_name: str,
        payload: dict[str, Any],
        conversation_id: str | None = None,
    ) -> AgentMessage:
        """Supervisor delegates a sub-task to a worker agent."""
        if worker_role not in self.worker_roles:
            raise ValueError(f"Role [{worker_role.value}] is not a worker member of this team.")

        msg = AgentMessage(
            organization_id=self.organization_id,
            conversation_id=conversation_id or f"team-task-{task_name}",
            sender_role=self.supervisor_role,
            recipient_role=worker_role,
            message_type=AgentMessageType.TASK_DELEGATION,
            payload={"task_name": task_name, **payload},
        )

        allowed, reason = self.detector.inspect_message(msg)
        if not allowed:
            raise PermissionError(f"Delegation rejected by collusion detector: {reason}")

        await self.bus.send(msg)
        return msg

    @abstractmethod
    async def execute_team_operation(self, operation_name: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Execute a coordinated team mission."""
        ...
