"""
Recruitment MCP Server — Candidate requisitions and applicant pipeline tools.
"""

from __future__ import annotations

from typing import Any

from backend.mcp.domain.models import MCPToolCallRequest, MCPToolContract
from backend.mcp.servers.base import MCPServer


class RecruitmentMCPServer(MCPServer):
    """Internal MCP server exposing recruitment pipeline and requisition status tools."""

    def __init__(self) -> None:
        super().__init__(
            server_id="recruitment-server",
            name="Recruitment ATS MCP Server",
            description="Inspects active job requisitions, applicant status, and interview rubrics.",
        )

    def _register_server_tools(self) -> None:
        self.register_tool(
            MCPToolContract(
                tool_id="recruitment.get_job_requisition",
                server_id=self.server_id,
                name="Get Job Requisition",
                description="Query job requisition requirements, mandatory qualifications, and open openings.",
                input_schema={"type": "object", "properties": {"job_id": {"type": "string"}}, "required": ["job_id"]},
                required_capabilities=["recruitment:read"],
                is_read_only=True,
            ),
            self._handle_get_job,
        )

    async def _handle_get_job(self, req: MCPToolCallRequest) -> dict[str, Any]:
        job_id = req.arguments.get("job_id", "job-default")
        return {
            "job_id": job_id,
            "title": "Lead Software Architect",
            "department": "Engineering",
            "required_skills": ["Python", "FastAPI", "Distributed Systems", "PostgreSQL"],
            "open_positions": 2,
            "status": "OPEN",
        }
