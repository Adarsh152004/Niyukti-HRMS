"""
Agent Tool Registry — Enums for Tool Categories.
"""

from __future__ import annotations

from enum import StrEnum


class ToolCategory(StrEnum):
    """Business category classification for Agent Tools."""

    EMPLOYEE = "EMPLOYEE"
    DEPARTMENT = "DEPARTMENT"
    DESIGNATION = "DESIGNATION"
    SKILL = "SKILL"
    DOCUMENT = "DOCUMENT"
    WORKFLOW = "WORKFLOW"
    ANALYTICS = "ANALYTICS"
    CUSTOM = "CUSTOM"
