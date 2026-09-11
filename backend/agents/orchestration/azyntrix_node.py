"""
Azyntrix Recruitment Agent Node — LangGraph Integration.

An isolated ReAct-style agent node that handles all Azyntrix-related requests:
  - Job posting / listing / updating / closing
  - Application pipeline management (status, notes, bulk ops)
  - Hiring funnel analytics and dashboard
  - Client inquiry review

This node is invoked by the main HRMS orchestrator (graph.py) when
the intent router classifies the query as AZYNTRIX_AGENT.
"""

from __future__ import annotations

import json
import logging
from typing import Any, AsyncIterator, Dict, Optional

from backend.agents.llm_gateway import default_gateway
from backend.agents.tools.azyntrix_tools import AZYNTRIX_TOOLS

logger = logging.getLogger("hrms.agents.orchestration.azyntrix_node")

# ─── Azyntrix Recruitment Coordinator System Prompt ───────────────────────────
AZYNTRIX_SYSTEM_PROMPT = """You are the Azyntrix Recruitment Coordinator AI — an intelligent hiring and talent operations agent for Azyntrix, a modern software solutions company.

You have FULL access to the Azyntrix platform's live data through your tools:

**Job Management Tools:**
- get_azyntrix_dashboard: Get live stats (jobs, applications, inquiries, conversion rate)
- list_job_openings: List all open/closed jobs, filter by department
- post_new_job: Create and publish new job listings
- update_job_description: Edit any field of an existing job
- close_job_opening: Close or permanently delete a job
- toggle_job_status: Flip a job between active and closed

**Application Pipeline Tools:**
- list_applications: View all candidate applications with filters
- advance_application_status: Move a candidate through: submitted → screening → interview_scheduled → offered / rejected
- bulk_advance_applications: Batch update multiple candidates at once
- add_application_note: Add reviewer notes without changing status
- list_client_inquiries: View incoming client project inquiries

**Operational Guidelines:**
- Always use real data from your tools — never fabricate IDs, counts, or names
- When creating a job, ask for details if not provided (title, department, description minimum)
- When advancing applications, confirm the action with a clear message showing candidate name and new stage
- Format responses in clean markdown with tables for listings
- For dashboard/stats questions, call get_azyntrix_dashboard first
- Department options: Frontend, Backend, Full Stack, Cloud & DevOps, Data & AI, Mobile, Security, QA & Testing, Product & Design, Engineering Leadership, Management, Sales & Marketing, Operations, HR & People
- Application stages in order: submitted → screening → interview_scheduled → offered OR rejected

Always respond professionally and concisely. Include job IDs and reference IDs in your responses so follow-up actions are possible.
"""

# ─── Intent Keywords for Router Classification ────────────────────────────────
AZYNTRIX_KEYWORDS = [
    # Job management
    "post a job", "post job", "create job", "create a job", "open a position",
    "add a role", "new job listing", "job requisition", "list jobs", "show jobs",
    "job openings", "open positions", "job posting", "close job", "close the job",
    "remove job", "deactivate job", "reactivate job", "toggle job", "update job",
    "edit job", "update the job", "modify job", "change job", "open jobs", "list open jobs",
    "open roles", "list open roles", "hiring roles", "all jobs", "available jobs",
    # Application management
    "applications", "who applied", "candidate", "applicants", "application pipeline",
    "screening", "interview", "advance application", "move application",
    "reject application", "accept application", "hire candidate", "offer candidate",
    "review applications", "application status", "update application",
    # Azyntrix specific
    "azyntrix dashboard", "azyntrix jobs", "azyntrix", "recruitment dashboard",
    "hiring funnel", "job listings", "hiring pipeline", "careers page",
    # Inquiries
    "client inquiries", "client leads", "project inquiries", "client contact",
    "inquiries", "new leads", "proposals",
]


def is_azyntrix_query(query: str) -> bool:
    """Returns True if the query should be routed to the Azyntrix agent."""
    lower = query.lower()
    return any(keyword in lower for keyword in AZYNTRIX_KEYWORDS)


async def run_azyntrix_agent(
    query: str,
    caller_role: str = "SUPERADMIN",
) -> AsyncIterator[Dict[str, Any]]:
    """
    Executes the Azyntrix recruitment agent with a ReAct-style tool loop.
    Yields structured SSE event frames compatible with the HRMS stream protocol.

    Supports:
    - Simple single-tool queries (dashboard, list jobs, list applications)
    - Multi-step operations (create job + confirm, advance application + add note)
    - Summarization over tool results
    """

    yield {
        "event": "thinking",
        "data": {
            "agent": "Azyntrix Recruitment Coordinator",
            "content": f"Analyzing your Azyntrix request: '{query[:80]}...' — preparing recruitment tools...",
        },
    }

    # Build tool name → callable map
    tool_map = {t.name: t for t in AZYNTRIX_TOOLS}

    # Build conversation: inject system prompt + user query
    conversation_messages = [
        {"role": "user", "content": query}
    ]

    # ReAct loop: max 4 iterations (tool call → result → next decision)
    MAX_ITERATIONS = 4
    tool_calls_made = []

    for iteration in range(MAX_ITERATIONS):
        # Ask the LLM what to do (with all tool results so far embedded in context)
        context_suffix = ""
        if tool_calls_made:
            context_suffix = "\n\nTool Results so far:\n" + "\n".join(
                f"[{tc['tool']}]: {json.dumps(tc['result'], indent=2)[:1500]}"
                for tc in tool_calls_made
            )

        system_with_context = AZYNTRIX_SYSTEM_PROMPT + context_suffix

        # Detect which tool to call based on query semantics + iteration state
        tool_to_call = _select_tool(query, iteration, tool_calls_made)

        if tool_to_call is None:
            # No more tool calls needed — generate final LLM response
            break

        tool_name = tool_to_call["name"]
        tool_args = tool_to_call["args"]

        if tool_name not in tool_map:
            logger.warning(f"[AzyntrixNode] Unknown tool: {tool_name}")
            break

        yield {
            "event": "tool_call",
            "data": {"tool": tool_name, "args": tool_args},
        }

        # Execute tool
        try:
            result = await tool_map[tool_name].ainvoke(tool_args)
            tool_calls_made.append({"tool": tool_name, "args": tool_args, "result": result})

            yield {
                "event": "tool_result",
                "data": {
                    "tool": tool_name,
                    "result": result if isinstance(result, dict) else {"data": result},
                },
            }
        except Exception as e:
            logger.error(f"[AzyntrixNode] Tool {tool_name} failed: {e}")
            yield {
                "event": "tool_result",
                "data": {
                    "tool": tool_name,
                    "error": str(e),
                    "result": {"success": False, "error": str(e)},
                },
            }
            tool_calls_made.append({"tool": tool_name, "args": tool_args, "result": {"error": str(e)}})
            break

    # Final LLM synthesis: generate natural language response from tool results
    yield {
        "event": "thinking",
        "data": {
            "agent": "Azyntrix Recruitment Coordinator",
            "content": "Synthesizing response from recruitment data...",
        },
    }

    tool_context = ""
    if tool_calls_made:
        tool_context = "\n\nReal-time data retrieved from Azyntrix platform:\n"
        for tc in tool_calls_made:
            tool_context += f"\n**{tc['tool']} result:**\n```json\n{json.dumps(tc['result'], indent=2)[:2000]}\n```\n"

    final_system = (
        f"{AZYNTRIX_SYSTEM_PROMPT}\n\n"
        f"Caller Role: {caller_role}\n"
        f"{tool_context}\n"
        f"Based on the above real data, provide a clear, professional, markdown-formatted response to the user's query."
    )

    messages = [{"role": "user", "content": query}]

    async for token in default_gateway.astream_chat(messages, system_instruction=final_system):
        yield {"event": "token", "data": {"text": token}}

    yield {
        "event": "done",
        "data": {
            "status": "SUCCESS",
            "agent": "Azyntrix Recruitment Coordinator",
            "tools_used": [tc["tool"] for tc in tool_calls_made],
        },
    }


def _select_tool(
    query: str,
    iteration: int,
    already_called: list,
) -> Optional[Dict[str, Any]]:
    """
    Deterministic tool selector: chooses the right tool based on query semantics.
    Returns None when no more tool calls are needed.
    """
    lower = query.lower()
    called_names = [tc["tool"] for tc in already_called]

    # First iteration: primary tool based on query type
    if iteration == 0:
        # Dashboard / overview
        if any(k in lower for k in ["dashboard", "overview", "stats", "summary", "how many", "total jobs", "total applications", "hiring funnel", "conversion"]):
            return {"name": "get_azyntrix_dashboard", "args": {}}

        # List jobs
        if any(k in lower for k in ["list job", "show job", "open position", "job opening", "available role", "what jobs", "all jobs"]):
            status = "closed" if "closed" in lower else "active"
            return {"name": "list_job_openings", "args": {"status": status, "limit": 20}}

        # Post new job
        if any(k in lower for k in ["post a job", "create a job", "add a job", "new job", "open a position", "create role", "post role"]):
            # Extract basic params from query heuristically
            return {"name": "post_new_job", "args": _extract_job_params(query)}

        # Close/delete job
        if any(k in lower for k in ["close job", "remove job", "deactivate job", "take down job", "filled position"]):
            return {"name": "list_job_openings", "args": {"status": "active", "limit": 50}}

        # Toggle job
        if any(k in lower for k in ["toggle job", "pause job", "reactivate job", "flip status"]):
            return {"name": "list_job_openings", "args": {"status": "active", "limit": 50}}

        # Applications
        if any(k in lower for k in ["applications", "who applied", "candidate", "applicant", "applied for"]):
            status_filter = None
            if "screening" in lower:
                status_filter = "screening"
            elif "interview" in lower:
                status_filter = "interview_scheduled"
            elif "offered" in lower:
                status_filter = "offered"
            elif "rejected" in lower:
                status_filter = "rejected"
            elif "submitted" in lower or "new" in lower:
                status_filter = "submitted"
            args = {"limit": 30}
            if status_filter:
                args["status"] = status_filter
            return {"name": "list_applications", "args": args}

        # Inquiries
        if any(k in lower for k in ["inquir", "client lead", "project proposal", "client contact"]):
            return {"name": "list_client_inquiries", "args": {"limit": 20}}

        # Azyntrix specific without clear sub-intent → dashboard
        if "azyntrix" in lower:
            return {"name": "get_azyntrix_dashboard", "args": {}}

    # No more tool calls needed
    return None


def _extract_job_params(query: str) -> Dict[str, Any]:
    """Extracts basic job parameters from a natural language query."""
    lower = query.lower()

    # Department detection
    department = "Backend"
    dept_map = {
        "frontend": "Frontend", "react": "Frontend", "vue": "Frontend", "angular": "Frontend",
        "backend": "Backend", "python": "Backend", "node": "Backend", "golang": "Backend",
        "full stack": "Full Stack", "fullstack": "Full Stack",
        "devops": "Cloud & DevOps", "cloud": "Cloud & DevOps", "aws": "Cloud & DevOps", "kubernetes": "Cloud & DevOps",
        "data": "Data & AI", "ml": "Data & AI", "ai": "Data & AI", "machine learning": "Data & AI",
        "mobile": "Mobile", "android": "Mobile", "ios": "Mobile", "flutter": "Mobile",
        "design": "Product & Design", "ux": "Product & Design", "ui": "Product & Design",
        "security": "Security", "qa": "QA & Testing", "testing": "QA & Testing",
        "product manager": "Management", "manager": "Management",
        "sales": "Sales & Marketing", "marketing": "Sales & Marketing",
        "hr": "HR & People", "people": "HR & People",
    }
    for key, val in dept_map.items():
        if key in lower:
            department = val
            break

    # Basic title extraction — grab what comes after common trigger phrases
    title = "Software Engineer"
    for trigger in ["post a job for", "create a job for", "add a role for", "open a position for", "post role for"]:
        if trigger in lower:
            title_raw = query[lower.find(trigger) + len(trigger):].strip()
            title = title_raw.split(".")[0].split(",")[0].strip().title()
            break

    return {
        "title": title,
        "department": department,
        "description": f"We are seeking a talented {title} to join the Azyntrix team.",
        "experience": "Mid Level",
        "salary_range": "Competitive",
        "location": "Remote (Worldwide)",
        "job_type": "Full-Time",
        "responsibilities": [],
        "requirements": [],
        "tech_stack": [],
        "is_active": True,
    }
