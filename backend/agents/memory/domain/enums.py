"""
Agent Memory — Enums for Memory Types.
"""

from __future__ import annotations

from enum import StrEnum


class MemoryType(StrEnum):
    """Classification of Agent Memory records."""

    TASK_CONTEXT = "TASK_CONTEXT"
    TOOL_RESULT = "TOOL_RESULT"
    CONVERSATION = "CONVERSATION"
    FACT = "FACT"
    DECISION = "DECISION"
    OBSERVATION = "OBSERVATION"
