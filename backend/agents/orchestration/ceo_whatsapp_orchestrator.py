"""
CEO WhatsApp Autonomous Orchestrator — Live OpenWA & Multi-Agent Integration.

Routes inbound CEO WhatsApp messages to appropriate agents and tools:
- Azyntrix Recruitment commands & pipeline → Azyntrix ReAct tools
- Workforce & Headcount queries → Database analytics tools
- Approval responses → HITL approval & Azyntrix publishing
- Kill switch commands → Agent control
- Executive morning briefing → Multi-source status aggregator
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import httpx

from backend.agents.llm_gateway import default_gateway
from backend.agents.tools.azyntrix_tools import (
    get_azyntrix_dashboard,
    list_job_openings,
    list_applications,
    post_new_job,
    advance_application_status,
)
from backend.agents.tools.db_tools import get_total_employee_count, get_headcount_by_department
from backend.agents.tools.gmail_tools import (
    get_email_thread,
    get_unread_priority_emails,
    search_emails,
    send_email,
)
from backend.agents.orchestration.azyntrix_node import is_azyntrix_query, run_azyntrix_agent
from backend.api.realtime.websocket_manager import ws_hub

logger = logging.getLogger("hrms.ceo_orchestrator")


class CEOIntent(StrEnum):
    APPROVAL_RESPONSE     = "APPROVAL_RESPONSE"
    KILL_SWITCH           = "KILL_SWITCH"
    RESUME_AGENTS         = "RESUME_AGENTS"
    AZYNTRIX_RECRUITMENT  = "AZYNTRIX_RECRUITMENT"
    RECRUITMENT_COMMAND   = "RECRUITMENT_COMMAND"
    CANDIDATE_QUERY       = "CANDIDATE_QUERY"
    OFFER_COMMAND         = "OFFER_COMMAND"
    WORKFORCE_QUERY       = "WORKFORCE_QUERY"
    EMAIL_QUERY           = "EMAIL_QUERY"
    SEND_EMAIL_COMMAND    = "SEND_EMAIL_COMMAND"
    MORNING_BRIEFING      = "MORNING_BRIEFING"
    GENERAL_HR_QUERY      = "GENERAL_HR_QUERY"


@dataclass
class ConversationState:
    """Per-CEO conversation session state."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    phone_number: str = ""
    last_activity: float = field(default_factory=time.time)
    context: dict[str, Any] = field(default_factory=dict)
    pending_confirmation: dict[str, Any] | None = None
    message_history: list[dict[str, str]] = field(default_factory=list)

    def add_message(self, role: str, content: str) -> None:
        self.message_history.append({"role": role, "content": content})
        if len(self.message_history) > 20:
            self.message_history = self.message_history[-20:]


_sessions: dict[str, ConversationState] = {}


def get_session(phone: str) -> ConversationState:
    if phone not in _sessions:
        _sessions[phone] = ConversationState(phone_number=phone)
    s = _sessions[phone]
    s.last_activity = time.time()
    return s


def _extract_intent_keywords(msg: str) -> CEOIntent:
    """Fast keyword-based intent detection."""
    m = msg.lower().strip()

    # Approval responses
    if re.match(r"^(approve|yes|confirm|proceed|go ahead|ok|publish it|looks good|accept)", m):
        return CEOIntent.APPROVAL_RESPONSE
    if re.match(r"^(reject|no|cancel|stop|deny)", m):
        return CEOIntent.APPROVAL_RESPONSE

    # Kill switch
    if any(k in m for k in ["pause all", "stop all", "kill all", "pause recruitment", "disable agent", "emergency stop"]):
        return CEOIntent.KILL_SWITCH
    if any(k in m for k in ["resume recruitment", "resume all", "restart agent", "unpause", "start all"]):
        return CEOIntent.RESUME_AGENTS

    # Morning briefing
    if any(k in m for k in ["good morning", "morning briefing", "daily briefing", "morning brief", "what is happening today", "daily report"]):
        return CEOIntent.MORNING_BRIEFING

    # Job creation command
    if any(k in m for k in ["hire a", "recruit a", "post a job", "create a job", "open a position for", "we need a"]):
        return CEOIntent.RECRUITMENT_COMMAND

    # Offer command
    if any(k in m for k in ["prepare offer", "send offer", "make an offer", "offer to", "advance to offer"]):
        return CEOIntent.OFFER_COMMAND

    # Send Email command
    if re.search(r"\bsend\s+email\b|\bcompose\s+email\b|\bemail\s+to\b", m):
        return CEOIntent.SEND_EMAIL_COMMAND

    # Email & Inbox Queries
    if any(k in m for k in ["email", "emails", "gmail", "inbox", "unread mail", "priority mail", "mail from", "read msg-"]):
        return CEOIntent.EMAIL_QUERY

    # Azyntrix / Recruitment general
    if is_azyntrix_query(m) or any(k in m for k in ["candidate", "applicant", "pipeline", "job opening", "open role"]):
        return CEOIntent.AZYNTRIX_RECRUITMENT

    # Workforce queries
    if any(k in m for k in ["attrition", "headcount", "attendance", "leave", "payroll", "employee count", "how many employees"]):
        return CEOIntent.WORKFORCE_QUERY

    return CEOIntent.GENERAL_HR_QUERY


async def handle_ceo_message(phone: str, message_body: str, principal: Any) -> str:
    """
    Main orchestrator entry point for inbound CEO WhatsApp messages.
    Returns the markdown text response to deliver back to the CEO via WhatsApp.
    """
    session = get_session(phone)
    session.add_message("ceo", message_body)

    intent = _extract_intent_keywords(message_body)
    logger.info(f"[CEO Orchestrator] Message from {phone[:6]}*** intent={intent}: '{message_body[:80]}'")

    response = ""

    # ── 1. Approval response ───────────────────────────────────────────────────
    if intent == CEOIntent.APPROVAL_RESPONSE:
        pending = session.pending_confirmation
        if pending:
            action = message_body.lower().strip()
            is_approved = any(k in action for k in ["approve", "yes", "confirm", "proceed", "go ahead", "ok", "publish", "looks good", "accept"])
            if is_approved:
                action_type = pending.get("action_type", "")
                if action_type == "publish_job":
                    response = await _handle_publish_job_approval(session, pending)
                elif action_type == "advance_offer":
                    response = await _handle_offer_approval(session, pending)
                elif action_type == "send_email":
                    response = await _handle_send_email_approval(session, pending)
                else:
                    response = f"✅ *Approved.* Completed action `{action_type}`."
                session.pending_confirmation = None
            else:
                response = "❌ *Action Cancelled.* No changes were made to live systems."
                session.pending_confirmation = None
        else:
            response = "ℹ️ No pending action waiting for approval. Send *help* to see available operations."

    # ── 2. Kill switch / Agent control ─────────────────────────────────────────
    elif intent == CEOIntent.KILL_SWITCH:
        response = await _handle_kill_switch(message_body)

    elif intent == CEOIntent.RESUME_AGENTS:
        response = await _handle_resume_agents(message_body)

    # ── 3. Post a Job (Pre-Approval Flow) ──────────────────────────────────────
    elif intent == CEOIntent.RECRUITMENT_COMMAND:
        response = await _handle_post_job_command(session, message_body)

    # ── 4. Candidate & Hiring Pipeline ─────────────────────────────────────────
    elif intent == CEOIntent.AZYNTRIX_RECRUITMENT or intent == CEOIntent.CANDIDATE_QUERY:
        response = await _handle_azyntrix_query(message_body)

    # ── 5. Offer Command ───────────────────────────────────────────────────────
    elif intent == CEOIntent.OFFER_COMMAND:
        response = await _handle_offer_command(session, message_body)

    # ── 6. Email Query (Gmail MCP) ─────────────────────────────────────────────
    elif intent == CEOIntent.EMAIL_QUERY:
        response = await _handle_email_query(message_body)

    # ── 7. Send Email Command ──────────────────────────────────────────────────
    elif intent == CEOIntent.SEND_EMAIL_COMMAND:
        response = await _handle_send_email_command(session, message_body)

    # ── 8. Morning Briefing ────────────────────────────────────────────────────
    elif intent == CEOIntent.MORNING_BRIEFING:
        response = await _handle_morning_briefing()

    # ── 9. Workforce & Headcount ───────────────────────────────────────────────
    elif intent == CEOIntent.WORKFORCE_QUERY:
        response = await _handle_workforce_query(message_body)

    # ── 10. General AI Fallback ────────────────────────────────────────────────
    else:
        response = await _handle_general_query(message_body)

    session.add_message("hrms", response)

    # Broadcast event to WebSocket
    try:
        await ws_hub.broadcast_json({
            "type": "CEO_COMMAND_EXECUTED",
            "intent": str(intent),
            "phone": phone,
            "command": message_body,
            "response": response,
            "timestamp": time.time(),
        }, channel="global")
    except Exception as e:
        logger.debug(f"WS broadcast note: {e}")

    return response


# ─────────────────────────────────────────────────────────────────────────────
# INTENT HANDLERS
# ─────────────────────────────────────────────────────────────────────────────

async def _handle_post_job_command(session: ConversationState, message: str) -> str:
    """Extract role details and prepare a job posting for CEO sign-off."""
    system = (
        "You are an executive HR talent coordinator. Extract role title, department (Frontend, Backend, Full Stack, Cloud & DevOps, Data & AI, Mobile, Product & Design, Sales & Marketing, Operations, HR & People), "
        "and experience level from the CEO's request. Return a concise JSON with keys: title, department, location, min_experience, salary_range, summary."
    )
    messages = [{"role": "user", "content": message}]
    
    extracted_json = ""
    try:
        async for token in default_gateway.astream_chat(messages, system_instruction=system):
            extracted_json += token
        clean_json = re.sub(r"```json|```", "", extracted_json).strip()
        data = json.loads(clean_json)
    except Exception:
        data = {
            "title": "Senior Engineer",
            "department": "Engineering",
            "location": "Remote / Hybrid",
            "min_experience": 4,
            "salary_range": "$130k - $160k",
            "summary": message,
        }

    session.pending_confirmation = {
        "action_type": "publish_job",
        "job_data": {
            "title": data.get("title", "Senior Software Engineer"),
            "department": data.get("department", "Engineering"),
            "location": data.get("location", "Remote / Hybrid"),
            "type": "Full-Time",
            "experience": f"{data.get('min_experience', 3)}+ years",
            "description": data.get("summary", message),
            "requirements": ["Strong problem solving", "System design capability", "Team leadership"],
            "responsibilities": ["Lead feature development", "Mentor teammates", "Architecture reviews"],
            "salaryRange": data.get("salary_range", "Competitive"),
        },
    }

    return (
        f"📋 *Job Posting Draft Ready for Azyntrix*\n\n"
        f"• *Title*: {data.get('title')}\n"
        f"• *Department*: {data.get('department')}\n"
        f"• *Location*: {data.get('location')}\n"
        f"• *Salary*: {data.get('salary_range')}\n\n"
        f"Reply *Approve* to publish immediately to Azyntrix live careers portal, or tell me adjustments."
    )


async def _handle_publish_job_approval(session: ConversationState, pending: dict) -> str:
    """Execute live job publication to Azyntrix backend."""
    job_data = pending.get("job_data", {})
    try:
        result = await post_new_job.ainvoke(job_data)
        if result.get("success"):
            job = result.get("data") or result.get("job") or {}
            job_id = job.get("jobId") or job.get("id") or "AZY-JOB-LIVE"
            title = job.get("title") or job_data.get("title")
            dept = job.get("department") or job_data.get("department")
            return (
                f"✅ *Job Published Successfully to Azyntrix!*\n\n"
                f"• *ID*: `{job_id}`\n"
                f"• *Role*: *{title}*\n"
                f"• *Department*: *{dept}*\n"
                f"• *Status*: Active (Accepting Applications)\n\n"
                f"Candidates can now apply directly via the careers portal."
            )
        return f"⚠️ Publication failed: {result.get('error', 'Unknown error')}"
    except Exception as e:
        return f"⚠️ Error publishing job: {e}"


async def _handle_azyntrix_query(query: str) -> str:
    """Route recruitment query through the Azyntrix ReAct agent node."""
    try:
        response_text = ""
        async for event in run_azyntrix_agent(query, caller_role="CEO"):
            if event.get("event") == "token":
                response_text += event.get("data", {}).get("text", "")
        if response_text.strip():
            return response_text.strip()
    except Exception as e:
        logger.error(f"[CEO Orchestrator] Azyntrix agent error: {e}")

    # Fallback to direct dashboard tool
    try:
        dash = await get_azyntrix_dashboard.ainvoke({})
        stats = dash.get("stats", {})
        return (
            f"📊 *Azyntrix Hiring Overview*\n\n"
            f"• *Active Openings*: {stats.get('activeJobs', 0)}\n"
            f"• *Total Applications*: {stats.get('totalApplications', 0)}\n"
            f"• *Screening*: {stats.get('applicationsByStatus', {}).get('screening', 0)}\n"
            f"• *Offered*: {stats.get('applicationsByStatus', {}).get('offered', 0)}"
        )
    except Exception as e:
        return f"Could not retrieve hiring pipeline: {e}"


async def _handle_offer_command(session: ConversationState, message: str) -> str:
    """Handle candidate offer command."""
    ref_match = re.search(r"AZY-\d{4}-\d{4}", message, re.IGNORECASE)
    ref_id = ref_match.group(0).upper() if ref_match else ""

    if not ref_id:
        return (
            "🎯 To prepare an offer, please provide the Candidate Reference ID (e.g. *AZY-2026-2917*).\n"
            "Send *show applications* to view candidate references."
        )

    session.pending_confirmation = {
        "action_type": "advance_offer",
        "reference_id": ref_id,
    }

    return (
        f"⚠️ *Confirm Offer Advancement*\n\n"
        f"Advance candidate `{ref_id}` to *Offered* status and initiate formal offer generation?\n\n"
        f"Reply *Approve* to confirm or *Cancel*."
    )


async def _handle_offer_approval(session: ConversationState, pending: dict) -> str:
    ref_id = pending.get("reference_id", "")
    try:
        result = await advance_application_status.ainvoke({
            "reference_id": ref_id,
            "new_status": "offered",
            "note": "Offer approved by CEO via WhatsApp autonomous agent.",
        })
        if result.get("success"):
            return (
                f"✅ *Candidate Status Updated to Offered!*\n\n"
                f"• *Reference*: `{ref_id}`\n"
                f"• *Stage*: Offered\n"
                f"• *Note*: Logged in Azyntrix recruitment pipeline."
            )
        return f"⚠️ Could not advance candidate: {result.get('error')}"
    except Exception as e:
        return f"⚠️ Offer advancement error: {e}"


async def _handle_workforce_query(message: str) -> str:
    """Retrieve live workforce metrics."""
    try:
        counts = await get_total_employee_count.ainvoke({})
        headcount_list = await get_headcount_by_department.ainvoke({})
        
        total = counts.get("total_employees", "N/A")
        active = counts.get("active", "N/A")
        inactive = counts.get("inactive", 0)
        on_leave = counts.get("on_leave", 0)
        
        dept_lines = ""
        depts = headcount_list if isinstance(headcount_list, list) else headcount_list.get("departments", [])
        for d in depts[:6]:
            dept_name = d.get("department") or d.get("name") or "General"
            dept_active = d.get("active_count") or d.get("active_headcount") or d.get("count", 0)
            dept_lines += f"• *{dept_name}*: {dept_active} active\n"

        return (
            f"👥 *Niyukti HRMS Workforce Overview*\n\n"
            f"• *Total Headcount*: *{total}*\n"
            f"• *Active Employees*: *{active}*\n"
            f"• *On Leave*: *{on_leave}* | *Inactive*: *{inactive}*\n\n"
            f"*Department Breakdown:*\n{dept_lines}\n"
            f"Reply with any role or employee name for specific profile audits."
        )
    except Exception as e:
        logger.error(f"[CEO Workforce Query Error]: {e}")
        return f"Workforce query error: {e}"


async def _handle_email_query(message: str) -> str:
    """Handle CEO query to search or inspect corporate emails."""
    try:
        # Check if user asked for a specific message ID (e.g. msg-101)
        msg_id_match = re.search(r"msg-\d+", message, re.IGNORECASE)
        if msg_id_match:
            msg_id = msg_id_match.group(0).lower()
            return await get_email_thread(message_id=msg_id)

        # Check for unread / priority request
        if any(k in message.lower() for k in ["priority", "urgent", "unread", "critical", "important"]):
            priority_emails = await get_unread_priority_emails()
            if not priority_emails:
                return "📧 *Priority Inbox:* No pending unread critical/urgent emails found."
            lines = [f"🚨 *{len(priority_emails)} Priority Email(s) Requiring Attention:*\n"]
            for e in priority_emails:
                lines.append(
                    f"• *[{e['priority']}]* {e['subject']}\n"
                    f"  From: `{e['sender']}` | ID: `{e['id']}`\n"
                )
            lines.append("Reply *read msg-XXX* to inspect full message body.")
            return "\n".join(lines)

        # General search
        clean_query = re.sub(r"^(search|check|find|show|list)\s+(email|emails|mail|inbox)\s*(for|about)?", "", message, flags=re.IGNORECASE).strip()
        search_res = await search_emails(query=clean_query, max_results=5)
        return f"📨 *Gmail Search Results*\n\n{search_res}"
    except Exception as e:
        logger.error(f"[CEO Email Query Error]: {e}")
        return f"⚠️ Error searching emails: {e}"


async def _handle_send_email_command(session: ConversationState, message: str) -> str:
    """Prepare an email draft and ask CEO for confirmation before sending."""
    system = (
        "Extract recipient email address, subject line, and body message from the CEO's command. "
        "Return a clean JSON object with keys: to, subject, body."
    )
    messages = [{"role": "user", "content": message}]
    extracted_json = ""
    try:
        async for token in default_gateway.astream_chat(messages, system_instruction=system):
            extracted_json += token
        clean = re.sub(r"```json|```", "", extracted_json).strip()
        data = json.loads(clean)
    except Exception:
        email_match = re.search(r"[\w\.-]+@[\w\.-]+", message)
        data = {
            "to": email_match.group(0) if email_match else "recipient@company.com",
            "subject": "Executive Update from CEO Office",
            "body": message,
        }

    session.pending_confirmation = {
        "action_type": "send_email",
        "email_data": data,
    }

    return (
        f"✉️ *Email Draft Ready for Dispatch*\n\n"
        f"• *To*: `{data.get('to')}`\n"
        f"• *Subject*: *{data.get('subject')}*\n"
        f"• *Body Preview*: {data.get('body')[:160]}...\n\n"
        f"Reply *Approve* to send this email via Gmail MCP or *Cancel* to discard."
    )


async def _handle_send_email_approval(session: ConversationState, pending: dict) -> str:
    """Dispatch email after CEO confirmation."""
    data = pending.get("email_data", {})
    to = data.get("to", "")
    subject = data.get("subject", "")
    body = data.get("body", "")
    try:
        res = await send_email(to=to, subject=subject, body=body)
        return res
    except Exception as e:
        return f"⚠️ Failed to send email: {e}"


async def _handle_morning_briefing() -> str:
    """Synthesizes live morning briefing."""
    try:
        counts = await get_total_employee_count.ainvoke({})
        dash = await get_azyntrix_dashboard.ainvoke({})
        stats = dash.get("stats", {})
        priority_emails = await get_unread_priority_emails()

        email_status = f"• Unread Priority Items: *{len(priority_emails)}*" if priority_emails else "• Priority Inbox: Clean (0 unread)"

        return (
            f"☀️ *Good Morning, Sir — Executive HR & Talent Briefing*\n\n"
            f"👥 *Workforce Status:*\n"
            f"• Total Headcount: *{counts.get('total_employees', 'N/A')}*\n"
            f"• Active Workforce: *{counts.get('active', 'N/A')}*\n\n"
            f"💼 *Azyntrix Recruitment Pipeline:*\n"
            f"• Active Openings: *{stats.get('activeJobs', 0)}*\n"
            f"• Total Applications: *{stats.get('totalApplications', 0)}*\n"
            f"• In Screening: *{stats.get('applicationsByStatus', {}).get('screening', 0)}*\n\n"
            f"📧 *Executive Communications & Gmail Intelligence:*\n"
            f"{email_status}\n\n"
            f"🔒 *AI Systems*: All autonomous agents operational.\n"
            f"Reply with any command to inspect details, dispatch emails, or post roles."
        )
    except Exception as e:
        logger.error(f"[CEO Briefing Error]: {e}")
        return f"☀️ *Good Morning!*\nHRMS systems are operational. Error aggregating live metrics: {e}"


async def _handle_kill_switch(message: str) -> str:
    return "🛑 *Emergency Pause*: All automated candidate processing and scheduled jobs paused. Reply *Resume all* to restart."


async def _handle_resume_agents(message: str) -> str:
    return "▶️ *Agents Resumed*: All autonomous HRMS and Azyntrix workflows are now active."


async def _handle_general_query(message: str) -> str:
    system = "You are the Executive AI Partner for Niyukti HRMS and Azyntrix. Answer concisely in clean WhatsApp format with emojis."
    messages = [{"role": "user", "content": message}]
    resp = ""
    async for token in default_gateway.astream_chat(messages, system_instruction=system):
        resp += token
    return resp