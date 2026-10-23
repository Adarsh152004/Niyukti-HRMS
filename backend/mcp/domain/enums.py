"""
MCP Domain Enums — Server statuses, tool categories, and access levels.
"""

from __future__ import annotations

from enum import StrEnum


class MCPServerStatus(StrEnum):
    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"
    QUARANTINED = "QUARANTINED"
    OFFLINE = "OFFLINE"


class MCPToolRiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
