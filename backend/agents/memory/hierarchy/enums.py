"""
Memory Hierarchy Enums — Tiers and Scopes for partitioned memory boundaries.
"""

from __future__ import annotations

from enum import StrEnum


class MemoryTier(StrEnum):
    """Hierarchical memory tier partitions."""

    AGENT = "AGENT"  # Private working scratchpad memory for single agent
    TEAM = "TEAM"  # Squad-shared memory for specialized collaborative agents
    ORGANIZATION = "ORGANIZATION"  # Company-wide authorized context and SOP state
    EMPLOYEE = "EMPLOYEE"  # Employee-specific private conversational & preference context
