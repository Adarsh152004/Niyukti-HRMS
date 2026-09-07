"""
Chat Response Envelope Schema.
Typed, validated UI contract separating conversational text from interactive domain widgets.
"""

from __future__ import annotations

import datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


WidgetType = Literal[
    "HEADCOUNT",
    "ATTENDANCE",
    "LEAVE_BALANCE",
    "TASK_SPRINT",
    "POLICY_CARD",
    "RECRUITMENT_PIPELINE",
    "PAYROLL_SUMMARY",
    "GENERIC_METRICS",
]


class WidgetPayload(BaseModel):
    widget_type: WidgetType = Field(..., description="Unique widget type identifier")
    version: int = Field(default=1, description="Schema version for this widget type")
    title: str = Field(..., description="Human-readable title of the widget")
    data: dict[str, Any] = Field(default_factory=dict, description="Structured data payload consumed by frontend widget renderer")


class ActionPayload(BaseModel):
    action_type: str = Field(..., description="e.g. 'PUNCH_IN', 'APPROVE_REQUISITION', 'VIEW_PAYSLIP'")
    action_id: str = Field(..., description="Unique ID for this action")
    label: str = Field(..., description="Display label for the button/action")
    endpoint: str = Field(..., description="API endpoint to trigger")
    method: Literal["GET", "POST", "PUT", "DELETE"] = Field(default="POST")
    payload: dict[str, Any] = Field(default_factory=dict, description="Request payload to submit")


class ChatResponseEnvelope(BaseModel):
    conversation_id: str = Field(..., description="Session or conversation thread ID")
    message_id: str = Field(..., description="Unique message ID")
    text: str = Field(..., description="Clean conversational answer or executive briefing text")
    role: Literal["user", "assistant", "system"] = Field(default="assistant")
    agent_role: Optional[str] = Field(None, description="e.g. 'CHRO Orchestrator', 'Recruitment Specialist'")
    widgets: list[WidgetPayload] = Field(default_factory=list, description="List of validated UI widgets to render")
    actions: list[ActionPayload] = Field(default_factory=list, description="Interactive action buttons")
    artifacts: list[dict[str, Any]] = Field(default_factory=list, description="Embedded document or approval cards")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Execution telemetry, timings, provider info")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
