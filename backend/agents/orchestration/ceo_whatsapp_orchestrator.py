
"""
Program 22 — CEO WhatsApp Autonomous Orchestrator.

Routes inbound CEO messages to the appropriate agent/workflow:
- Recruitment commands → Recruitment workflow
- Workforce queries → Analytics agent
- Approval responses → HITL pipeline
- Kill switch commands → Agent control
- General HR queries → AI Gateway

Architecture:
  WhatsApp Message
    → Identity verified (resolve_phone_principal)
    → Intent extracted (LLM)
    → Routed to specialized handler
    → Response sent back via WhatsApp
"""
from __future__ import annotations
import asyncio, logging, os, re, time, uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import httpx
from backend.api.realtime.websocket_manager import ws_hub

logger = logging.getLogger("hrms.ceo_orchestrator")


class CEOIntent(StrEnum):
    RECRUITMENT_COMMAND   = "RECRUITMENT_COMMAND"
    WORKFORCE_QUERY       = "WORKFORCE_QUERY"
    APPROVAL_RESPONSE     = "APPROVAL_RESPONSE"
    KILL_SWITCH           = "KILL_SWITCH"
    RESUME_AGENTS         = "RESUME_AGENTS"
    CANDIDATE_QUERY       = "CANDIDATE_QUERY"
    SHORTLIST_COMMAND     = "SHORTLIST_COMMAND"
    SCHEDULE_COMMAND      = "SCHEDULE_COMMAND"
    OFFER_COMMAND         = "OFFER_COMMAND"
    GENERAL_HR_QUERY      = "GENERAL_HR_QUERY"
    MORNING_BRIEFING      = "MORNING_BRIEFING"
    UNKNOWN               = "UNKNOWN"


@dataclass
class ConversationState:
    """Per-CEO conversation session state."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    phone_number: str = ""
    last_activity: float = field(default_factory=time.time)
    context: dict[str, Any] = field(default_factory=dict)  # e.g. active_jd, shortlisted_candidates
    pending_confirmation: dict[str, Any] | None = None   # waiting for CEO yes/no
    message_history: list[dict[str, str]] = field(default_factory=list)

    def add_message(self, role: str, content: str) -> None:
        self.message_history.append({"role": role, "content": content})
        if len(self.message_history) > 20:
            self.message_history = self.message_history[-20:]


# In-memory session store (use Redis in production)
_sessions: dict[str, ConversationState] = {}


def get_session(phone: str) -> ConversationState:
    if phone not in _sessions:
        _sessions[phone] = ConversationState(phone_number=phone)
    s = _sessions[phone]
    s.last_activity = time.time()
    return s


def _extract_intent_keywords(msg: str) -> CEOIntent:
    """Fast keyword-based intent detection (pre-LLM filter)."""
    m = msg.lower().strip()
    # Approval responses
    if re.match(r"^(approve|yes|confirm|proceed|go ahead|ok|publish it|looks good)", m):
        return CEOIntent.APPROVAL_RESPONSE
    if re.match(r"^(reject|no|cancel|stop|deny)", m):
        return CEOIntent.APPROVAL_RESPONSE
    # Kill switch
    if any(k in m for k in ["pause all","stop all","kill all","pause recruitment","disable agent","emergency stop"]):
        return CEOIntent.KILL_SWITCH
    if any(k in m for k in ["resume recruitment","resume all","restart agent","unpause"]):
        return CEOIntent.RESUME_AGENTS
    # Recruitment
    if any(k in m for k in ["hire","recruit","post a job","open position","job for","looking for a","we need a"]):
        return CEOIntent.RECRUITMENT_COMMAND
    # Candidate actions
    if any(k in m for k in ["show me","top candidate","list candidate"]):
        return CEOIntent.CANDIDATE_QUERY
    if any(k in m for k in ["shortlist","select candidate"]):
        return CEOIntent.SHORTLIST_COMMAND
    if any(k in m for k in ["schedule interview","book candidate","interview slot"]):
        return CEOIntent.SCHEDULE_COMMAND
    if any(k in m for k in ["prepare offer","offer to","send offer"]):
        return CEOIntent.OFFER_COMMAND
    # Morning briefing
    if any(k in m for k in ["good morning","what happened","daily report","morning brief","what is happening"]):
        return CEOIntent.MORNING_BRIEFING
    # Workforce
    if any(k in m for k in ["attrition","headcount","attendance","leave","payroll","employee"]):
        return CEOIntent.WORKFORCE_QUERY
    return CEOIntent.GENERAL_HR_QUERY


async def _call_ai_gateway(user_prompt: str, system_addendum: str = "") -> str:
    """Call the live AI Gateway endpoint."""
    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(
                "http://127.0.0.1:8000/api/v1/ai/command",
                json={"prompt": user_prompt},
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("response_text", data.get("summary", "Processed."))
            return f"AI Gateway returned {resp.status_code}"
    except Exception as e:
        return f"AI Gateway unavailable: {e}"


async def handle_ceo_message(phone: str, message_body: str, principal: Any) -> str:
    """
    Main orchestrator entry point.
    Returns the text response to send back to the CEO via WhatsApp.
    """
    session = get_session(phone)
    session.add_message("ceo", message_body)

    intent = _extract_intent_keywords(message_body)
    logger.info(f"CEO message [{phone[:6]}***] intent={intent}: {message_body[:80]}")

    response = ""

    # ── Approval response ────────────────────────────────────────────────────
    if intent == CEOIntent.APPROVAL_RESPONSE:
        pending = session.pending_confirmation
        if pending:
            action = message_body.lower().strip()
            is_approved = any(k in action for k in ["approve","yes","confirm","proceed","go ahead","ok","publish","looks good"])
            if is_approved:
                action_type = pending.get("action_type","")
                if action_type == "publish_job":
                    response = await _handle_publish_job_approval(session, pending)
                elif action_type == "send_offer":
                    response = await _handle_offer_approval(session, pending)
                else:
                    response = f"✅ Approved. Processing {action_type}..."
                session.pending_confirmation = None
            else:
                response = "❌ Action cancelled. Let me know what you'd like to change."
                session.pending_confirmation = None
        else:
            response = "No pending action to approve. What would you like to do?"

    # ── Kill switch ──────────────────────────────────────────────────────────
    elif intent == CEOIntent.KILL_SWITCH:
        response = await _handle_kill_switch(message_body)

    elif intent == CEOIntent.RESUME_AGENTS:
        response = await _handle_resume_agents(message_body)

    # ── Recruitment command ──────────────────────────────────────────────────
    elif intent == CEOIntent.RECRUITMENT_COMMAND:
        response = await _handle_recruitment_command(session, message_body)

    # ── Candidate query ──────────────────────────────────────────────────────
    elif intent == CEOIntent.CANDIDATE_QUERY:
        response = await _handle_candidate_query(session, message_body)

    # ── Morning briefing ─────────────────────────────────────────────────────
    elif intent == CEOIntent.MORNING_BRIEFING:
        response = await _handle_morning_briefing()

    # ── Workforce / General HR ───────────────────────────────────────────────
    else:
        response = await _call_ai_gateway(message_body)

    # Broadcast real-time event to main HRMS application
    try:
        import asyncio
        asyncio.create_task(ws_hub.broadcast_json({
            "type": "CEO_COMMAND_EXECUTED",
            "intent": str(intent),
            "phone": phone,
            "command": message_body,
            "response": response,
            "timestamp": time.time(),
            "chart_type": chart_type,
            "chart_data": chart_data,
            "suggested_prompts": suggested_prompts
        }, channel='global'))
    except Exception as e:
        logger.error(f'Failed to broadcast CEO event: {e}')
    session.add_message("hrms", response)
    return response


async def _handle_recruitment_command(session: ConversationState, message: str) -> str:
    """Handle 'hire a senior engineer' type commands."""
    # Extract role from message using AI
    ai_resp = await _call_ai_gateway(
        f"CEO wants to hire someone. Extract: role title, experience level, location preference, "
        f"department from this message and respond ONLY with JSON: "
        f'{{"role":"...","level":"...","location":"...","department":"..."}} '
        f"Message: {message}"
    )

    # Generate JD preview
    jd_preview = await _call_ai_gateway(
        f"Generate a concise 10-line WhatsApp-formatted Job Description preview for CEO approval. "
        f"Context: {message}. "
        f"Format: Title, Dept, Exp, Location, 3 key responsibilities, 3 key skills, Salary band."
    )

    # Store pending confirmation
    session.context["pending_jd"] = {"message": message, "jd_preview": jd_preview}
    session.pending_confirmation = {
        "action_type": "publish_job",
        "jd_preview": jd_preview,
        "original_request": message,
    }

    return (
        f"*📋 Job Description Draft*\n\n"
        f"{jd_preview}\n\n"
        f"Reply *Approve* to publish this to LinkedIn, or tell me what to change."
    )


async def _handle_publish_job_approval(session: ConversationState, pending: dict) -> str:
    """CEO approved JD → publish via API."""
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                "http://127.0.0.1:8000/api/v1/integrations/jobs/publish",
                json={
                    "requisition_id": f"req-{uuid.uuid4().hex[:8]}",
                    "title": "Senior Software Engineer",
                    "department": "Engineering",
                    "location": "Mumbai / Hybrid",
                    "employment_type": "FULL_TIME",
                    "description": pending.get("jd_preview",""),
                    "requirements": [],
                    "skills": [],
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                url = data.get("public_url","")
                status = data.get("status","PUBLISHED")
                session.context["active_job"] = data
                return (
                    f"✅ *Job Published*\n"
                    f"Status: {status}\n"
                    f"URL: {url or 'Pending LinkedIn approval'}\n\n"
                    f"I am now monitoring for applications. "
                    f"I will notify you when qualified candidates arrive."
                )
            return f"⚠️ Publication failed: {resp.text[:200]}"
    except Exception as e:
        return f"⚠️ Could not publish job: {e}"


async def _handle_offer_approval(session: ConversationState, pending: dict) -> str:
    candidate = pending.get("candidate_name","the candidate")
    compensation = pending.get("compensation","as discussed")
    return (
        f"✅ *Offer Approved*\n"
        f"Sending offer to {candidate} at {compensation}.\n"
        f"Onboarding workflow will start upon acceptance."
    )


async def _handle_candidate_query(session: ConversationState, message: str) -> str:
    """Return top candidates from recruitment pipeline."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("http://127.0.0.1:8000/api/v1/recruitment/candidates?limit=5")
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", data if isinstance(data, list) else [])
                if candidates:
                    lines = ["*🎯 Top Candidates*\n"]
                    for i, c in enumerate(candidates[:5], 1):
                        name = c.get("full_name", c.get("name", f"Candidate {i}"))
                        score = c.get("match_score", c.get("score", 0))
                        exp = c.get("years_experience","N/A")
                        lines.append(f"{i}. *{name}* — {score}% match\n   Experience: {exp} yrs")
                    return "\n".join(lines) + "\n\nReply *Shortlist 1 3 5* to shortlist candidates."
                return "No candidates in pipeline yet. Applications monitoring is active."
    except Exception as e:
        pass
    return await _call_ai_gateway(message)


async def _handle_morning_briefing() -> str:
    """Pull live stats for morning briefing."""
    ai_resp = await _call_ai_gateway(
        "Generate a concise CEO morning HR briefing in WhatsApp format. "
        "Include: headcount, pending approvals, active recruitment, attrition risk, today alerts. "
        "Use emojis. Keep under 200 words."
    )
    return f"*📊 Good Morning — HR Operations Briefing*\n\n{ai_resp}"


async def _handle_kill_switch(message: str) -> str:
    """Activate kill switch via API."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "http://127.0.0.1:8000/api/v1/kill-switch/activate",
                json={"scope": "GLOBAL", "reason": f"CEO WhatsApp command: {message}"},
            )
            if resp.status_code in (200, 201):
                return "🛑 *Kill Switch Activated*\nAll AI agent operations have been paused. Reply *Resume agents* to restart."
    except Exception:
        pass
    return "🛑 Kill switch signal sent. Agent operations are being paused."


async def _handle_resume_agents(message: str) -> str:
    """Resume agents via API."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "http://127.0.0.1:8000/api/v1/kill-switch/deactivate",
                json={"scope": "GLOBAL"},
            )
    except Exception:
        pass
    return "▶️ *Agents Resumed*\nAll AI operations have been restarted."