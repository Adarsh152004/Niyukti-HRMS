"""
Context Budget Allocator — Manages token quotas across prompt components.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ContextSegment(StrEnum):
    SYSTEM = "SYSTEM"
    SECURITY = "SECURITY"
    AGENT_POLICY = "AGENT_POLICY"
    TASK = "TASK"
    PLAN = "PLAN"
    MEMORY = "MEMORY"
    RAG = "RAG"
    TOOLS = "TOOLS"
    RECENT_RESULTS = "RECENT_RESULTS"


@dataclass
class SegmentBudget:
    max_tokens: int
    reserved_tokens: int
    allow_truncation: bool
    priority: int  # Higher priority segments are preserved first


class ContextBudgetAllocator:
    """Allocates token budgets to ensure safety invariants and prevent context starvation."""

    DEFAULT_LIMITS = {
        "FAST_ECONOMY": 4096,
        "BALANCED": 8192,
        "HIGH_REASONING": 32768,
    }

    def get_budgets(self, max_context_tokens: int = 8192) -> dict[ContextSegment, SegmentBudget]:
        """
        Produce deterministic token allocation rules for context assembly.
        Security and Agent Policy segments are non-truncatable with priority 100.
        """
        return {
            ContextSegment.SYSTEM: SegmentBudget(
                max_tokens=int(max_context_tokens * 0.10), reserved_tokens=200, allow_truncation=False, priority=90
            ),
            ContextSegment.SECURITY: SegmentBudget(
                max_tokens=int(max_context_tokens * 0.15), reserved_tokens=300, allow_truncation=False, priority=100
            ),
            ContextSegment.AGENT_POLICY: SegmentBudget(
                max_tokens=int(max_context_tokens * 0.15), reserved_tokens=300, allow_truncation=False, priority=95
            ),
            ContextSegment.TASK: SegmentBudget(
                max_tokens=int(max_context_tokens * 0.15), reserved_tokens=200, allow_truncation=False, priority=80
            ),
            ContextSegment.PLAN: SegmentBudget(
                max_tokens=int(max_context_tokens * 0.10), reserved_tokens=100, allow_truncation=True, priority=70
            ),
            ContextSegment.MEMORY: SegmentBudget(
                max_tokens=int(max_context_tokens * 0.15), reserved_tokens=100, allow_truncation=True, priority=50
            ),
            ContextSegment.RAG: SegmentBudget(
                max_tokens=int(max_context_tokens * 0.20), reserved_tokens=200, allow_truncation=True, priority=60
            ),
            ContextSegment.TOOLS: SegmentBudget(
                max_tokens=int(max_context_tokens * 0.10), reserved_tokens=150, allow_truncation=True, priority=65
            ),
            ContextSegment.RECENT_RESULTS: SegmentBudget(
                max_tokens=int(max_context_tokens * 0.15), reserved_tokens=150, allow_truncation=True, priority=75
            ),
        }
