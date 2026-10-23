"""
Azyntrix HRMS Agent Tools — Full Programmatic Access Layer.

Provides LangChain @tool decorated functions that give the HRMS AI Agent
complete control over the Azyntrix platform:
  - Fetching, creating, updating, closing Job Descriptions
  - Managing candidate application pipeline (status, notes, bulk ops)
  - Analytics dashboard access
  - Contact inquiries review

All tools communicate with the Azyntrix backend REST API at http://localhost:5050
using the AGENT_API_KEY for authentication.

Usage:
    from backend.agents.tools.azyntrix_tools import (
        get_azyntrix_dashboard,
        list_job_openings,
        post_new_job,
        update_job_description,
        close_job_opening,
        list_applications,
        advance_application_status,
        bulk_advance_applications,
        add_application_note,
        list_client_inquiries,
    )
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

import httpx
from langchain_core.tools import tool

logger = logging.getLogger("hrms.agents.tools.azyntrix")

# ─── Configuration ─────────────────────────────────────────────────────────────
AZYNTRIX_BASE_URL = os.getenv("AZYNTRIX_API_URL", "http://localhost:5050/api/v1/agent")
AGENT_API_KEY = os.getenv("AGENT_API_KEY", "azyntrix-agent-dev-key-2026")
REQUEST_TIMEOUT = 15.0

def _agent_headers() -> dict[str, str]:
    """Return auth headers for all agent API calls."""
    return {
        "X-Agent-Key": AGENT_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

async def _agent_get(path: str, params: dict | None = None) -> dict[str, Any]:
    """Perform a GET request to the Azyntrix agent API."""
    url = f"{AZYNTRIX_BASE_URL}{path}"
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        resp = await client.get(url, headers=_agent_headers(), params=params or {})
        resp.raise_for_status()
        return resp.json()

async def _agent_post(path: str, body: dict) -> dict[str, Any]:
    """Perform a POST request to the Azyntrix agent API."""
    url = f"{AZYNTRIX_BASE_URL}{path}"
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        resp = await client.post(url, headers=_agent_headers(), json=body)
        resp.raise_for_status()
        return resp.json()

async def _agent_put(path: str, body: dict) -> dict[str, Any]:
    """Perform a PUT request to the Azyntrix agent API."""
    url = f"{AZYNTRIX_BASE_URL}{path}"
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        resp = await client.put(url, headers=_agent_headers(), json=body)
        resp.raise_for_status()
        return resp.json()

async def _agent_patch(path: str, body: dict) -> dict[str, Any]:
    """Perform a PATCH request to the Azyntrix agent API."""
    url = f"{AZYNTRIX_BASE_URL}{path}"
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        resp = await client.patch(url, headers=_agent_headers(), json=body)
        resp.raise_for_status()
        return resp.json()

async def _agent_delete(path: str, params: dict | None = None) -> dict[str, Any]:
    """Perform a DELETE request to the Azyntrix agent API."""
    url = f"{AZYNTRIX_BASE_URL}{path}"
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        resp = await client.delete(url, headers=_agent_headers(), params=params or {})
        resp.raise_for_status()
        return resp.json()


# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICS TOOLS
# ─────────────────────────────────────────────────────────────────────────────

@tool
async def get_azyntrix_dashboard() -> dict[str, Any]:
    """
    Retrieve the full Azyntrix HRMS dashboard with real-time stats.

    Returns key metrics including:
    - Total jobs (active/closed split)
    - Applications by pipeline status (submitted, screening, interview_scheduled, offered, rejected)
    - Conversion rate (applications → offers)
    - Total client inquiries
    - Recent applications (last 5)
    - Top jobs by applicant count

    Use this when asked: "show me the dashboard", "how many applications do we have",
    "what is the hiring funnel", "give me an overview of our recruitment status".
    """
    try:
        result = await _agent_get("/dashboard")
        logger.info("[AzyntrixTools] Dashboard fetched successfully.")
        return result
    except Exception as e:
        logger.error(f"[AzyntrixTools] Dashboard fetch failed: {e}")
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# JOB LISTING TOOLS
# ─────────────────────────────────────────────────────────────────────────────

@tool
async def list_job_openings(
    status: Optional[str] = "active",
    department: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
) -> dict[str, Any]:
    """
    List all job openings on the Azyntrix careers platform.

    Args:
        status: Filter by 'active', 'closed', or omit for all jobs.
        department: Filter by department name (e.g. 'Frontend', 'Backend',
                    'Cloud & DevOps', 'Product & Design', 'Data & AI', 'Mobile').
        limit: Number of results per page (default 20, max 50).
        page: Page number for pagination (default 1).

    Use this when asked: "what jobs are open", "list our job postings",
    "show positions in Frontend department", "how many roles are we hiring for".
    """
    try:
        params = {"limit": limit, "page": page}
        if status:
            params["status"] = status
        if department:
            params["department"] = department
        result = await _agent_get("/jobs", params=params)
        logger.info(f"[AzyntrixTools] Listed {result.get('count', 0)} jobs.")
        return result
    except Exception as e:
        logger.error(f"[AzyntrixTools] Job listing failed: {e}")
        return {"success": False, "error": str(e)}


@tool
async def post_new_job(
    title: str,
    department: str,
    description: str,
    experience: str = "Mid Level",
    salary_range: str = "Competitive",
    location: str = "Remote (Worldwide)",
    job_type: str = "Full-Time",
    responsibilities: Optional[list[str]] = None,
    requirements: Optional[list[str]] = None,
    tech_stack: Optional[list[str]] = None,
    is_active: bool = True,
) -> dict[str, Any]:
    """
    Post a new job listing on the Azyntrix careers platform.

    Args:
        title: Job title (e.g. "Senior React Engineer", "Lead DevOps Architect").
        department: Department name. Valid values: 'Frontend', 'Backend', 'Full Stack',
                    'Cloud & DevOps', 'Data & AI', 'Mobile', 'Security', 'QA & Testing',
                    'Product & Design', 'Engineering Leadership', 'Management',
                    'Sales & Marketing', 'Operations', 'HR & People'.
        description: Detailed job description (at least 2-3 sentences).
        experience: Experience level e.g. "3-5 Years", "5+ Years", "8+ Years".
        salary_range: Compensation range e.g. "$120,000 – $160,000 USD".
        location: Work location (default: "Remote (Worldwide)").
        job_type: Employment type e.g. "Full-Time", "Contract", "Part-Time".
        responsibilities: List of job responsibility strings.
        requirements: List of requirement/qualification strings.
        tech_stack: List of technologies/skills required.
        is_active: Whether the job should be publicly visible (default True).

    Use this when asked: "post a new job for X", "create a job listing for Y role",
    "add a new position for Z engineer", "open a new job requisition".
    """
    try:
        body = {
            "title": title,
            "department": department,
            "description": description,
            "experience": experience,
            "salaryRange": salary_range,
            "location": location,
            "type": job_type,
            "responsibilities": responsibilities or [],
            "requirements": requirements or [],
            "techStack": tech_stack or [],
            "isActive": is_active,
        }
        result = await _agent_post("/jobs", body=body)
        logger.info(f"[AzyntrixTools] Job posted: {result.get('data', {}).get('id')}")
        return result
    except Exception as e:
        logger.error(f"[AzyntrixTools] Job posting failed: {e}")
        return {"success": False, "error": str(e)}


@tool
async def update_job_description(
    job_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    salary_range: Optional[str] = None,
    experience: Optional[str] = None,
    location: Optional[str] = None,
    responsibilities: Optional[list[str]] = None,
    requirements: Optional[list[str]] = None,
    tech_stack: Optional[list[str]] = None,
    is_active: Optional[bool] = None,
) -> dict[str, Any]:
    """
    Update an existing job listing on the Azyntrix platform.

    Args:
        job_id: The unique job ID (e.g. "senior-fullstack-web-architect").
                Use list_job_openings() first to get valid job IDs.
        title: New job title (optional).
        description: New job description (optional).
        salary_range: Updated salary range (optional).
        experience: Updated experience requirement (optional).
        location: Updated work location (optional).
        responsibilities: Updated responsibilities list (optional).
        requirements: Updated requirements list (optional).
        tech_stack: Updated technology stack list (optional).
        is_active: Set to True to reactivate or False to close (optional).

    Use this when asked: "update the salary for job X", "add Python to the tech stack for Y role",
    "change the experience requirement for Z position", "rewrite the description for job X".
    """
    try:
        body = {}
        if title is not None:
            body["title"] = title
        if description is not None:
            body["description"] = description
        if salary_range is not None:
            body["salaryRange"] = salary_range
        if experience is not None:
            body["experience"] = experience
        if location is not None:
            body["location"] = location
        if responsibilities is not None:
            body["responsibilities"] = responsibilities
        if requirements is not None:
            body["requirements"] = requirements
        if tech_stack is not None:
            body["techStack"] = tech_stack
        if is_active is not None:
            body["isActive"] = is_active

        result = await _agent_put(f"/jobs/{job_id}", body=body)
        logger.info(f"[AzyntrixTools] Job updated: {job_id}")
        return result
    except Exception as e:
        logger.error(f"[AzyntrixTools] Job update failed for {job_id}: {e}")
        return {"success": False, "error": str(e)}


@tool
async def close_job_opening(
    job_id: str,
    permanent: bool = False,
) -> dict[str, Any]:
    """
    Close or permanently delete a job listing from the Azyntrix careers page.

    Args:
        job_id: The unique job ID. Use list_job_openings() first to get valid IDs.
        permanent: If True, permanently deletes the job (irreversible).
                   If False (default), performs a soft-close (job is hidden but recoverable).

    Use this when asked: "close the job for X position", "remove the Y listing",
    "take down the Z role", "we've filled this position", "hide this job posting".
    """
    try:
        params = {"hardDelete": "true" if permanent else "false"}
        result = await _agent_delete(f"/jobs/{job_id}", params=params)
        logger.info(f"[AzyntrixTools] Job closed/deleted: {job_id} (permanent={permanent})")
        return result
    except Exception as e:
        logger.error(f"[AzyntrixTools] Job close failed for {job_id}: {e}")
        return {"success": False, "error": str(e)}


@tool
async def toggle_job_status(job_id: str) -> dict[str, Any]:
    """
    Toggle a job listing between active (publicly visible) and closed (hidden) status.

    Args:
        job_id: The unique job ID. Use list_job_openings() to find valid IDs.

    Use this when asked: "pause job X", "reactivate job Y",
    "temporarily hide this posting", "flip the status of job Z".
    """
    try:
        result = await _agent_patch(f"/jobs/{job_id}/toggle", body={})
        logger.info(f"[AzyntrixTools] Job status toggled: {job_id}")
        return result
    except Exception as e:
        logger.error(f"[AzyntrixTools] Toggle failed for {job_id}: {e}")
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# APPLICATION PIPELINE TOOLS
# ─────────────────────────────────────────────────────────────────────────────

@tool
async def list_applications(
    job_id: Optional[str] = None,
    status: Optional[str] = None,
    email: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
) -> dict[str, Any]:
    """
    List candidate applications with optional filters.

    Args:
        job_id: Filter by specific job ID (optional).
        status: Filter by pipeline status. Valid values: 'submitted', 'screening',
                'interview_scheduled', 'offered', 'rejected' (optional).
        email: Filter by candidate email (partial match) (optional).
        limit: Results per page (default 20).
        page: Page number (default 1).

    Use this when asked: "show me all applications", "list candidates for job X",
    "who applied for the backend role", "show me applications in screening",
    "how many candidates are in interview stage".
    """
    try:
        params = {"limit": limit, "page": page}
        if job_id:
            params["jobId"] = job_id
        if status:
            params["status"] = status
        if email:
            params["email"] = email
        result = await _agent_get("/applications", params=params)
        logger.info(f"[AzyntrixTools] Listed {result.get('count', 0)} applications.")
        return result
    except Exception as e:
        logger.error(f"[AzyntrixTools] Application listing failed: {e}")
        return {"success": False, "error": str(e)}


@tool
async def advance_application_status(
    reference_id: str,
    new_status: str,
    reviewer_note: Optional[str] = None,
    reviewer_name: str = "HRMS AI Agent",
) -> dict[str, Any]:
    """
    Update a candidate's application pipeline status and optionally add a reviewer note.

    Args:
        reference_id: Application reference ID (e.g. "AZY-2026-1234").
                      Use list_applications() to find valid reference IDs.
        new_status: Target pipeline stage. Valid values:
                    'submitted' → 'screening' → 'interview_scheduled' → 'offered' / 'rejected'
        reviewer_note: Optional note explaining the decision or next steps.
        reviewer_name: Name of the reviewer (default: "HRMS AI Agent").

    Use this when asked: "move application AZY-2026-1234 to screening",
    "advance John Doe to interview", "reject application X",
    "mark candidate Y as offered", "update status for reference Z".
    """
    try:
        body = {
            "status": new_status,
            "reviewerName": reviewer_name,
        }
        if reviewer_note:
            body["reviewerNote"] = reviewer_note
        result = await _agent_patch(f"/applications/{reference_id}/status", body=body)
        logger.info(f"[AzyntrixTools] Application {reference_id} moved to {new_status}")
        return result
    except Exception as e:
        logger.error(f"[AzyntrixTools] Status update failed for {reference_id}: {e}")
        return {"success": False, "error": str(e)}


@tool
async def bulk_advance_applications(
    reference_ids: list[str],
    new_status: str,
    reviewer_note: Optional[str] = None,
    reviewer_name: str = "HRMS AI Agent",
) -> dict[str, Any]:
    """
    Bulk update multiple candidate applications to the same pipeline status at once.

    Args:
        reference_ids: List of application reference IDs (e.g. ["AZY-2026-1234", "AZY-2026-5678"]).
        new_status: Target pipeline stage for all specified applications.
                    Valid values: 'submitted', 'screening', 'interview_scheduled', 'offered', 'rejected'.
        reviewer_note: Optional note applied to all updated applications.
        reviewer_name: Name of the reviewer (default: "HRMS AI Agent").

    Use this when asked: "reject all these applications: X, Y, Z",
    "move these candidates to screening: A, B, C",
    "bulk advance these applications to interview".
    """
    try:
        body = {
            "referenceIds": reference_ids,
            "status": new_status,
            "reviewerName": reviewer_name,
        }
        if reviewer_note:
            body["reviewerNote"] = reviewer_note
        result = await _agent_post("/applications/bulk-status", body=body)
        logger.info(f"[AzyntrixTools] Bulk updated {len(reference_ids)} applications → {new_status}")
        return result
    except Exception as e:
        logger.error(f"[AzyntrixTools] Bulk update failed: {e}")
        return {"success": False, "error": str(e)}


@tool
async def add_application_note(
    reference_id: str,
    note: str,
    author: str = "HRMS AI Agent",
) -> dict[str, Any]:
    """
    Add a reviewer note to a candidate application without changing its status.

    Args:
        reference_id: Application reference ID (e.g. "AZY-2026-1234").
        note: The note content to add (e.g. "Strong system design answers. Recommend fast-tracking.").
        author: Name of the person or system adding the note (default: "HRMS AI Agent").

    Use this when asked: "add a note to application X", "annotate this candidate's profile",
    "leave a comment on application Y saying Z", "flag this application for review".
    """
    try:
        body = {"note": note, "author": author}
        result = await _agent_post(f"/applications/{reference_id}/note", body=body)
        logger.info(f"[AzyntrixTools] Note added to application {reference_id}")
        return result
    except Exception as e:
        logger.error(f"[AzyntrixTools] Note addition failed for {reference_id}: {e}")
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# CLIENT INQUIRIES TOOLS
# ─────────────────────────────────────────────────────────────────────────────

@tool
async def list_client_inquiries(
    status: Optional[str] = None,
    limit: int = 20,
    page: int = 1,
) -> dict[str, Any]:
    """
    List client project discovery inquiries submitted via the Azyntrix contact form.

    Args:
        status: Filter by inquiry status. Valid values: 'pending_review', 'under_scoping',
                'proposal_sent', 'active_client', 'archived' (optional).
        limit: Results per page (default 20).
        page: Page number (default 1).

    Use this when asked: "show me client inquiries", "who has reached out to us",
    "list pending project proposals", "how many new client leads do we have".
    """
    try:
        params = {"limit": limit, "page": page}
        if status:
            params["status"] = status
        result = await _agent_get("/inquiries", params=params)
        logger.info(f"[AzyntrixTools] Listed {result.get('count', 0)} inquiries.")
        return result
    except Exception as e:
        logger.error(f"[AzyntrixTools] Inquiry listing failed: {e}")
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# TOOL REGISTRY - for dynamic discovery
# ─────────────────────────────────────────────────────────────────────────────

AZYNTRIX_TOOLS = [
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
]

__all__ = [
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
