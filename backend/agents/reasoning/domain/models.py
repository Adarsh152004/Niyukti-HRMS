"""
Agent Reasoning — Domain Models for Decisions, Provider Requests/Responses, and Runs.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.agents.reasoning.domain.enums import DecisionType


class ReasoningDecision(BaseModel):
    """
    Pydantic-validated structured decision emitted by the LLM reasoning provider.
    """

    decision_type: DecisionType = Field(description="Decision category: ANSWER, TOOL_CALL, etc.")
    goal: str = Field(default="", description="Current sub-goal being addressed")
    explanation: str = Field(default="", description="Concise explanation for decision")
    selected_tool: str | None = Field(default=None, description="Tool ID if decision_type is TOOL_CALL")
    tool_arguments: dict[str, Any] = Field(default_factory=dict, description="Arguments for tool call")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    requires_human: bool = Field(default=False)
    final_response: str | None = Field(default=None, description="Final response string if ANSWER or COMPLETE")
    next_step: str | None = Field(default=None)


class LLMRequest(BaseModel):
    """
    Request object sent to an LLMProviderPort.
    """

    system_prompt: str
    user_prompt: str
    tools: list[dict[str, Any]] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
    step_number: int = 1


class LLMResponse(BaseModel):
    """
    Response object received from an LLMProviderPort.
    """

    raw_output: str
    parsed_decision: ReasoningDecision | None = Field(default=None)
    token_usage: dict[str, int] = Field(default_factory=dict)
    latency_ms: int = 0


class ReasoningRun(BaseModel):
    """
    Audit record tracking a single autonomous reasoning execution run.
    """

    run_id: str = Field(default_factory=lambda: f"run-{uuid.uuid4()}")
    organization_id: str
    agent_id: str
    task_id: str
    status: str = Field(default="RUNNING", description="RUNNING, COMPLETED, FAILED, WAITING_APPROVAL")
    step_count: int = 0
    duration_ms: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    completed_at: datetime | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)
