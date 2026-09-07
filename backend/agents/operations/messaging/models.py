"""
Typed Multi-Agent Messaging Models — Defines structured message envelope for inter-agent communication.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from backend.agents.specialized.domain.enums import SpecializedAgentRole


class AgentMessageType(StrEnum):
    """Types of structured inter-agent messages."""

    TASK_DELEGATION = "TASK_DELEGATION"
    TASK_RESULT = "TASK_RESULT"
    STATUS_QUERY = "STATUS_QUERY"
    STATUS_REPLY = "STATUS_REPLY"
    SUPERVISOR_ARBITRATION = "SUPERVISOR_ARBITRATION"
    ESCALATION = "ESCALATION"
    KNOWLEDGE_SHARE = "KNOWLEDGE_SHARE"


class AgentMessagePriority(StrEnum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AgentMessage(BaseModel):
    """
    Structured typed envelope for communication between specialized AI HR agents.
    """

    message_id: str = Field(default_factory=lambda: f"msg-{uuid.uuid4()}")
    conversation_id: str = Field(default_factory=lambda: f"conv-{uuid.uuid4()}")
    organization_id: str = Field(description="Tenant isolation boundary")
    sender_role: SpecializedAgentRole
    recipient_role: SpecializedAgentRole
    message_type: AgentMessageType
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: AgentMessagePriority = Field(default=AgentMessagePriority.NORMAL)
    in_reply_to: str | None = Field(default=None)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)
