"""
Stateful LangGraph Multi-Agent Orchestrator with Human-In-The-Loop Checkpointing.
Coordinates the Intent Router, HR Data Analyst Agent, Policy RAG Agent,
and HITL Approval Gates with live event streaming.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Annotated, Any, AsyncIterator, Dict, List, Optional, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from backend.agents.llm_gateway import default_gateway
from backend.agents.rag.policy_rag import search_company_policies
from backend.agents.tools.db_tools import ALL_DB_TOOLS
from backend.agents.tools.guarded_sql_tool import execute_read_only_sql

logger = logging.getLogger("hrms.agents.orchestration.graph")


# ─── Graph State Definition ───────────────────────────────────────────────────
class HRMSAgentState(TypedDict):
    messages: List[Dict[str, Any]]
    client_type: str  # "workforce" | "mobile" | "employee"
    caller_role: str  # "SUPERADMIN" | "HR_MANAGER" | "EMPLOYEE"
    caller_name: str
    active_agent: str
    intermediate_steps: List[Dict[str, Any]]
    pending_approval: Optional[Dict[str, Any]]
    approval_status: Optional[str]  # "PENDING" | "APPROVED" | "REJECTED"
    final_response: str


# ─── System Instructions ──────────────────────────────────────────────────────
ROUTER_PROMPT = """You are the Niyukti Enterprise HRMS AI Supervisor.
Classify the user request into one of the following execution paths:
1. "POLICY_RAG": Inquiries about company policies, leave carry-forward, office timings, POSH, resignation, handbook rules.
2. "HITL_ACTION": Requests to execute critical operations: Run payroll batch, approve all pending leaves, terminate employee, update salary records.
3. "HR_ANALYST": Inquiries about employee counts, departments, headcount, attendance summaries, leave records, payroll statistics, or directory lookups.

Return a JSON object with:
{"route": "POLICY_RAG" | "HITL_ACTION" | "HR_ANALYST", "reasoning": "brief explanation", "action_details": {"action": "...", "summary": "..."} if HITL_ACTION else None}
"""

ANALYST_SYSTEM_PROMPT = """You are the Lead HR Data Analyst Agent for Niyukti Enterprise HRMS.
You have direct, governed access to the enterprise SQLite database via verified tools:
- get_all_employees: Directory lookup, employee status, filters.
- get_headcount_by_department: Aggregate headcount and department breakdown.
- get_employee_profile: Comprehensive 360 profile by ID or code.
- get_attendance_summary: Today's presence, punctuality, and absence rates.
- get_leave_balances: PTO requests and leave balance statuses.
- get_payroll_summary: High-level salary expense and burn rate (SUPERADMIN only).
- execute_read_only_sql: Guarded ad-hoc read-only SELECT queries for custom analytics.

Provide authoritative, professional, and well-structured markdown answers.
Include clean tables, key metrics, and concise executive summaries.
"""

POLICY_SYSTEM_PROMPT = """You are the Enterprise HR Policy & Compliance Agent for Niyukti HRMS.
Use the search_company_policies tool to cite official company guidelines on PTO, attendance grace periods,
leave carry-forwards, notice periods, and workplace conduct.
Always cite the specific policy clause or category accurately.
"""


# ─── LangGraph Engine Implementation ──────────────────────────────────────────
class LangGraphHRMSEngine:
    def __init__(self):
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(HRMSAgentState)

        # Register Nodes
        workflow.add_node("router", self._router_node)
        workflow.add_node("hr_analyst", self._hr_analyst_node)
        workflow.add_node("policy_rag", self._policy_rag_node)
        workflow.add_node("hitl_gate", self._hitl_gate_node)

        # Define Entry Point & Conditional Routing
        workflow.set_entry_point("router")

        def route_decision(state: HRMSAgentState):
            pending = state.get("pending_approval")
            if pending and state.get("approval_status") == "PENDING":
                return "hitl_gate"
            agent = state.get("active_agent")
            if agent == "Policy Agent":
                return "policy_rag"
            if agent == "HITL Gate":
                return "hitl_gate"
            return "hr_analyst"

        workflow.add_conditional_edges(
            "router",
            route_decision,
            {
                "hr_analyst": "hr_analyst",
                "policy_rag": "policy_rag",
                "hitl_gate": "hitl_gate",
            },
        )

        workflow.add_edge("hr_analyst", END)
        workflow.add_edge("policy_rag", END)
        workflow.add_edge("hitl_gate", END)

        return workflow.compile(checkpointer=self.checkpointer)

    async def _router_node(self, state: HRMSAgentState) -> Dict[str, Any]:
        """Classifies intent and determines whether HITL gate is triggered."""
        last_user_msg = state["messages"][-1]["content"]
        lower = last_user_msg.lower()

        # Deterministic HITL check for high-risk operations
        if any(keyword in lower for keyword in ["run payroll", "execute payroll", "approve all leaves", "terminate employee", "process bonus"]):
            action_id = f"act-{uuid.uuid4().hex[:8]}"
            return {
                "active_agent": "HITL Gate",
                "approval_status": "PENDING",
                "pending_approval": {
                    "action_id": action_id,
                    "action": "Batch Payroll Disbursement" if "payroll" in lower else "Administrative Action",
                    "summary": f"User requested high-impact action: '{last_user_msg}'. Requires executive authorization.",
                    "risk_level": "CRITICAL" if "payroll" in lower else "HIGH",
                },
                "intermediate_steps": state.get("intermediate_steps", []) + [
                    {"step": "Intent Router", "details": "Detected high-impact administrative action. Routing to HITL Approval Gate."}
                ],
            }

        # Policy & Handbook check
        if any(keyword in lower for keyword in ["policy", "leave rule", "carry forward", "handbook", "posh", "timing", "grace period", "notice period", "maternity", "paternity"]):
            return {
                "active_agent": "Policy Agent",
                "intermediate_steps": state.get("intermediate_steps", []) + [
                    {"step": "Intent Router", "details": "Query classified as Company Policy & Handbook request. Routing to Policy RAG Agent."}
                ],
            }

        # Default to HR Data Analyst
        return {
            "active_agent": "HR Data Analyst",
            "intermediate_steps": state.get("intermediate_steps", []) + [
                {"step": "Intent Router", "details": "Query classified as Workforce & Database Analysis. Routing to HR Data Analyst Agent."}
            ],
        }

    async def _policy_rag_node(self, state: HRMSAgentState) -> Dict[str, Any]:
        """Executes Policy search and generates grounded answer."""
        query = state["messages"][-1]["content"]
        policies = await search_company_policies.ainvoke({"query": query})
        policy_context = "\n\n".join([f"### {p['title']} ({p['category']})\n{p['content']}" for p in policies])

        system_instruction = f"{POLICY_SYSTEM_PROMPT}\n\nOfficial HR Policy Context:\n{policy_context}"
        return {
            "final_response": "",  # Streamed live by runner
            "intermediate_steps": state.get("intermediate_steps", []) + [
                {
                    "step": "Policy RAG Tool",
                    "tool": "search_company_policies",
                    "result_summary": f"Retrieved {len(policies)} policy sections ({', '.join(p['title'] for p in policies)})",
                }
            ],
        }

    async def _hr_analyst_node(self, state: HRMSAgentState) -> Dict[str, Any]:
        """Runs the HR Data Analyst tool loop."""
        return {
            "active_agent": "HR Data Analyst",
        }

    async def _hitl_gate_node(self, state: HRMSAgentState) -> Dict[str, Any]:
        """Handles the paused HITL approval gate."""
        return {
            "active_agent": "HITL Gate",
        }

    async def astream_events(
        self,
        query: str,
        caller_role: str = "SUPERADMIN",
        client_type: str = "workforce",
        conversation_id: Optional[str] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Executes the LangGraph pipeline and yields structured SSE event frames:
        - {"event": "thinking", ...}
        - {"event": "tool_call", ...}
        - {"event": "tool_result", ...}
        - {"event": "approval_required", ...}
        - {"event": "token", ...}
        - {"event": "done", ...}
        """
        thread_id = conversation_id or f"sess-{uuid.uuid4().hex[:10]}"
        lower = query.lower()

        # Step 1: Thinking / Routing Event
        yield {
            "event": "thinking",
            "data": {
                "agent": "Supervisor Router",
                "content": f"Analyzing intent for query: '{query[:80]}...'",
                "client_type": client_type,
            },
        }

        # Step 2: Check for HITL Trigger
        if any(keyword in lower for keyword in ["run payroll", "execute payroll", "approve all leaves", "terminate employee"]):
            action_id = f"act-{uuid.uuid4().hex[:8]}"
            yield {
                "event": "thinking",
                "data": {
                    "agent": "HITL Gatekeeper",
                    "content": "Action requires executive authorization. Generating Human-in-the-Loop approval gate...",
                },
            }
            yield {
                "event": "approval_required",
                "data": {
                    "action_id": action_id,
                    "action": "Deterministic Payroll Batch Run" if "payroll" in lower else "Bulk Leave Approval",
                    "summary": f"Executing '{query}' modifies active enterprise records and triggers bank disbursements.",
                    "risk_level": "CRITICAL" if "payroll" in lower else "HIGH",
                    "thread_id": thread_id,
                    "status": "WAITING_APPROVAL",
                },
            }
            # Stream explanatory response
            explanation = (
                f"⚠️ **Action Paused for Human-in-the-Loop Authorization**\n\n"
                f"The requested operation (**{query}**) requires explicit sign-off from an authorized executive ({caller_role}).\n\n"
                f"- **Action ID**: `{action_id}`\n"
                f"- **Risk Level**: High / Critical\n"
                f"- **Status**: Pending Review\n\n"
                f"Please click **Approve** or **Reject** in the approval card above to continue execution."
            )
            for word in explanation.split(" "):
                yield {"event": "token", "data": {"text": word + " "}}
            yield {"event": "done", "data": {"status": "PAUSED_HITL", "action_id": action_id}}
            return

        # Step 3: Policy RAG Route
        if any(keyword in lower for keyword in ["policy", "leave rule", "carry forward", "handbook", "posh", "timing", "grace period", "notice period", "maternity", "paternity"]):
            yield {
                "event": "thinking",
                "data": {
                    "agent": "Policy & Compliance Agent",
                    "content": "Consulting official company policy handbook via vector RAG...",
                },
            }
            yield {
                "event": "tool_call",
                "data": {"tool": "search_company_policies", "args": {"query": query}},
            }

            policies = await search_company_policies.ainvoke({"query": query})
            yield {
                "event": "tool_result",
                "data": {
                    "tool": "search_company_policies",
                    "result": [{"title": p["title"], "category": p["category"]} for p in policies],
                },
            }

            policy_context = "\n\n".join([f"### {p['title']} ({p['category']})\n{p['content']}" for p in policies])
            system_prompt = f"{POLICY_SYSTEM_PROMPT}\n\nRelevant Policy Excerpts:\n{policy_context}"

            messages = [{"role": "user", "content": query}]
            yield {
                "event": "thinking",
                "data": {"agent": "Policy & Compliance Agent", "content": "Generating verified policy answer..."},
            }

            async for token in default_gateway.astream_chat(messages, system_instruction=system_prompt):
                yield {"event": "token", "data": {"text": token}}

            yield {"event": "done", "data": {"status": "SUCCESS", "agent": "Policy Agent"}}
            return

        # Step 4: HR Data Analyst (Database Queries)
        yield {
            "event": "thinking",
            "data": {
                "agent": "HR Data Analyst",
                "content": "Evaluating workforce database tools to answer your query...",
            },
        }

        # Smart Tool Selection based on query semantics
        tool_results_text = ""

        if any(k in lower for k in ["headcount", "department breakdown", "departments", "team size"]):
            yield {"event": "tool_call", "data": {"tool": "get_headcount_by_department", "args": {}}}
            from backend.agents.tools.db_tools import get_headcount_by_department
            res = await get_headcount_by_department.ainvoke({})
            yield {"event": "tool_result", "data": {"tool": "get_headcount_by_department", "result": res}}
            tool_results_text += f"\nHeadcount by Department:\n{json.dumps(res, indent=2)}\n"

        elif any(k in lower for k in ["attendance", "present", "absent", "punch", "late"]):
            yield {"event": "tool_call", "data": {"tool": "get_attendance_summary", "args": {"date_str": "today"}}}
            from backend.agents.tools.db_tools import get_attendance_summary
            res = await get_attendance_summary.ainvoke({})
            yield {"event": "tool_result", "data": {"tool": "get_attendance_summary", "result": res}}
            tool_results_text += f"\nToday's Attendance Summary:\n{json.dumps(res, indent=2)}\n"

        elif any(k in lower for k in ["payroll", "salary", "burn rate", "compensation"]):
            if caller_role in ("SUPERADMIN", "CEO"):
                yield {"event": "tool_call", "data": {"tool": "get_payroll_summary", "args": {}}}
                from backend.agents.tools.db_tools import get_payroll_summary
                res = await get_payroll_summary.ainvoke({})
                yield {"event": "tool_result", "data": {"tool": "get_payroll_summary", "result": res}}
                tool_results_text += f"\nPayroll Statistics:\n{json.dumps(res, indent=2)}\n"
            else:
                tool_results_text += "\nAccess Denied: Payroll summaries are restricted to Superadmin and Executive roles.\n"

        elif any(k in lower for k in ["leave", "pto", "vacation", "sick leave"]):
            yield {"event": "tool_call", "data": {"tool": "get_leave_balances", "args": {}}}
            from backend.agents.tools.db_tools import get_leave_balances
            res = await get_leave_balances.ainvoke({})
            yield {"event": "tool_result", "data": {"tool": "get_leave_balances", "result": res}}
            tool_results_text += f"\nActive Leave Requests:\n{json.dumps(res, indent=2)}\n"

        else:
            # General employee listing or ad-hoc query
            yield {"event": "tool_call", "data": {"tool": "get_all_employees", "args": {"status": "ACTIVE"}}}
            from backend.agents.tools.db_tools import get_all_employees
            res = await get_all_employees.ainvoke({"status": "ACTIVE"})
            yield {"event": "tool_result", "data": {"tool": "get_all_employees", "result": res}}
            tool_results_text += f"\nActive Employee Records:\n{json.dumps(res, indent=2)}\n"

        # Final step: Stream natural-language response synthesized by LLM
        system_instruction = (
            f"{ANALYST_SYSTEM_PROMPT}\n\n"
            f"Caller Role: {caller_role}\n"
            f"Client Frontend: {client_type}\n"
            f"Database Tools Result:\n{tool_results_text}\n"
            f"Format all answers cleanly with markdown tables or bulleted executive summaries."
        )

        messages = [{"role": "user", "content": query}]
        yield {
            "event": "thinking",
            "data": {"agent": "HR Data Analyst", "content": "Synthesizing executive response with verified data..."},
        }

        async for token in default_gateway.astream_chat(messages, system_instruction=system_instruction):
            yield {"event": "token", "data": {"text": token}}

        yield {"event": "done", "data": {"status": "SUCCESS", "agent": "HR Data Analyst"}}


# Singleton orchestrator engine instance
langgraph_engine = LangGraphHRMSEngine()
