"""
Agent Tools Package Exports.
"""

from __future__ import annotations

from backend.agents.tools.application.tool_discovery import ToolDiscovery
from backend.agents.tools.application.tool_gateway import ToolExecutionGateway
from backend.agents.tools.application.tool_registry import ToolRegistry
from backend.agents.tools.domain.enums import ToolCategory
from backend.agents.tools.domain.models import ToolDefinition, ToolExecutionResult, ToolProposal
from backend.agents.tools.azyntrix_tools import (
    AZYNTRIX_TOOLS,
    get_azyntrix_dashboard,
    list_job_openings,
    post_new_job,
    update_job_description,
    close_job_opening,
    toggle_job_status,
    list_applications,
    advance_application_status,
    bulk_advance_applications,
    add_application_note,
    list_client_inquiries,
)

__all__ = [
    "ToolCategory",
    "ToolDefinition",
    "ToolDiscovery",
    "ToolExecutionGateway",
    "ToolExecutionResult",
    "ToolProposal",
    "ToolRegistry",
    # Azyntrix Integration Tools
    "AZYNTRIX_TOOLS",
    "get_azyntrix_dashboard",
    "list_job_openings",
    "post_new_job",
    "update_job_description",
    "close_job_opening",
    "toggle_job_status",
    "list_applications",
    "advance_application_status",
    "bulk_advance_applications",
    "add_application_note",
    "list_client_inquiries",
]

