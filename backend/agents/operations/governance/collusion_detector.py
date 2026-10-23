"""
Agent Collusion & Privilege Escalation Detector — Validates inter-agent message flows against hierarchical authority.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from backend.agents.operations.messaging.models import AgentMessage, AgentMessageType
from backend.agents.specialized.domain.enums import SpecializedAgentRole

logger = logging.getLogger(__name__)


class CollusionViolationType(StrEnum):
    UNAUTHORIZED_DELEGATION = "UNAUTHORIZED_DELEGATION"
    PEER_COLLUSION = "PEER_COLLUSION"
    CIRCULAR_MESSAGE_STORM = "CIRCULAR_MESSAGE_STORM"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"


@dataclass
class CollusionAlert:
    organization_id: str
    violation_type: CollusionViolationType
    sender_role: SpecializedAgentRole
    recipient_role: SpecializedAgentRole
    message_id: str
    details: str
    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class CollusionDetector:
    """
    Monitors and enforces hierarchical delegation governance across multi-agent teams.
    """

    _instance: CollusionDetector | None = None

    def __init__(self) -> None:
        self._alerts: list[CollusionAlert] = []
        self._conversation_chain_depth: dict[str, int] = defaultdict(int)

        # Supervisors definition
        self._supervisors: set[SpecializedAgentRole] = {
            SpecializedAgentRole.EXECUTIVE_HR_AGENT,
            SpecializedAgentRole.HR_MANAGER_AGENT,
            SpecializedAgentRole.RECRUITMENT_AGENT,
        }

    @classmethod
    def get_instance(cls) -> CollusionDetector:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def inspect_message(self, message: AgentMessage) -> tuple[bool, str | None]:
        """
        Evaluate an inter-agent message.
        Returns: (allowed: bool, rejection_reason: str | None)
        """
        # 1. Check Task Delegation Hierarchy: Only supervisors can issue TASK_DELEGATION
        if message.message_type == AgentMessageType.TASK_DELEGATION and message.sender_role not in self._supervisors:
            alert = CollusionAlert(
                organization_id=message.organization_id,
                violation_type=CollusionViolationType.UNAUTHORIZED_DELEGATION,
                sender_role=message.sender_role,
                recipient_role=message.recipient_role,
                message_id=message.message_id,
                details=f"Worker agent [{message.sender_role.value}] attempted unauthorized task delegation to [{message.recipient_role.value}] without supervisor authorization.",
            )
            self._alerts.append(alert)
            logger.warning(f"Collusion blocked: {alert.details}")
            return False, alert.details

        # 2. Check Circular Message Storms
        self._conversation_chain_depth[message.conversation_id] += 1
        if self._conversation_chain_depth[message.conversation_id] > 20:
            alert = CollusionAlert(
                organization_id=message.organization_id,
                violation_type=CollusionViolationType.CIRCULAR_MESSAGE_STORM,
                sender_role=message.sender_role,
                recipient_role=message.recipient_role,
                message_id=message.message_id,
                details=f"Excessive message chain depth ({self._conversation_chain_depth[message.conversation_id]}) in conversation [{message.conversation_id}] indicating potential deadlock or storm.",
            )
            self._alerts.append(alert)
            return False, alert.details

        return True, None

    def get_alerts(self, organization_id: str | None = None) -> list[CollusionAlert]:
        """Return audit alerts."""
        if organization_id:
            return [a for a in self._alerts if a.organization_id == organization_id]
        return list(self._alerts)
