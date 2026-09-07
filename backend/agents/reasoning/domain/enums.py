"""
Agent Reasoning — Enums for Decision Types.
"""

from __future__ import annotations

from enum import StrEnum


class DecisionType(StrEnum):
    """Structured decision type output by LLM reasoning provider."""

    ANSWER = "ANSWER"
    TOOL_CALL = "TOOL_CALL"
    ASK_CLARIFICATION = "ASK_CLARIFICATION"
    REQUEST_APPROVAL = "REQUEST_APPROVAL"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"
