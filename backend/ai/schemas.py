"""
AI-Powered Intelligent HRMS — Structured AI Reasoning & Decision Schemas.

Enforces strict Pydantic parsing of all LLM model outputs.
Free-form, unvalidated markdown or raw text outputs are rejected.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any
from pydantic import BaseModel, Field


class DecisionType(StrEnum):
    INFORMATIONAL = "INFORMATIONAL"
    TOOL_PROPOSAL = "TOOL_PROPOSAL"
    WORKFLOW_DISPATCH = "WORKFLOW_DISPATCH"
    HITL_ESCALATION = "HITL_ESCALATION"
    ABSTAIN = "ABSTAIN"


class ToolProposal(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    rationale: str
    required_capability: str = "HRMS_QUERY"
    risk_level: str = "LOW"
    requires_approval: bool = False


class ReasoningDecision(BaseModel):
    decision_type: DecisionType
    summary: str
    confidence: float = Field(ge=0.0, le=1.0)
    tool_proposal: ToolProposal | None = None
    requires_approval: bool = False
    risk_level: str = "LOW"
    citations: list[str] = Field(default_factory=list)
    suggested_visualization: str | None = None  # e.g., "bar_chart", "table", "timeline"
    final_response: str
