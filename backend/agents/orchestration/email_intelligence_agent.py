"""
Program 23 — Autonomous Proactive Email Intelligence Agent for CEO.

Continuously monitors Gmail inbox via Gmail MCP Tools, classifies critical HR events
(Offer Acceptances, Resignations, Compliance Deadlines, Legal Alerts),
and automatically synthesizes executive briefings pushed directly to the CEO's chat channel
without requiring manual prompts.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any

from backend.agents.llm_gateway import default_gateway
from backend.agents.tools.gmail_tools import (
    get_unread_priority_emails,
    mark_email_reported,
    search_emails,
)
from backend.api.realtime.websocket_manager import ws_hub

logger = logging.getLogger("hrms.email_intelligence")


class EmailIntelligenceAgent:
    """
    Autonomous Agent that continuously watches email, reasons on business impact,
    and proactively notifies the CEO in real-time.
    """

    def __init__(self, check_interval_seconds: int = 45):
        self.interval = check_interval_seconds
        self._running = False
        self._task: asyncio.Task | None = None
        self._recent_reports: list[dict[str, Any]] = []

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop(), name="email-intelligence-worker")
        logger.info(f"🚀 Autonomous Email Intelligence Agent STARTED (polling every {self.interval}s)")

    async def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Autonomous Email Intelligence Agent STOPPED")

    async def _monitor_loop(self) -> None:
        # Initial wait for server bootstrap
        await asyncio.sleep(5)
        while self._running:
            try:
                await self.triage_and_dispatch_proactive_reports()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[Email Intelligence] Error in monitor loop: {e}", exc_info=True)
            await asyncio.sleep(self.interval)

    async def triage_and_dispatch_proactive_reports(self) -> list[dict[str, Any]]:
        """
        Poll unread priority emails, synthesize action briefings, and proactively alert CEO.
        """
        unread_emails = await get_unread_priority_emails()
        if not unread_emails:
            return []

        generated_reports: list[dict[str, Any]] = []

        for email in unread_emails:
            email_id = email["id"]
            sender = email["sender"]
            subject = email["subject"]
            body = email["body"]
            priority = email.get("priority", "HIGH")

            # 1. Synthesize Executive Action Briefing via LLM
            prompt = (
                f"You are the Executive AI Chief of Staff for the CEO of Apex Enterprise / Azyntrix.\n"
                f"Analyze this critical inbound email and write a concise, high-impact CEO Briefing.\n\n"
                f"From: {sender}\n"
                f"Subject: {subject}\n"
                f"Body: {body}\n\n"
                f"Output your response strictly in the following format:\n"
                f"🚨 [CATEGORY / EVENT TITLE]\n"
                f"• Sender: <sender>\n"
                f"• Key Highlight: <1-2 sentences on what happened>\n"
                f"• Business Impact: <impact on revenue, headcount, hiring, or compliance>\n"
                f"• Recommended Next Step: <recommended action for the CEO>\n"
            )

            try:
                briefing_text = await default_gateway.generate(
                    prompt=prompt,
                    system_prompt="You are a decisive executive chief of staff. Be clear, succinct, and actionable.",
                    temperature=0.2,
                )
            except Exception as e:
                logger.warning(f"LLM triage fallback for {email_id}: {e}")
                briefing_text = (
                    f"🚨 CRITICAL EMAIL NOTIFICATION\n"
                    f"• Sender: {sender}\n"
                    f"• Subject: {subject}\n"
                    f"• Priority: {priority}\n"
                    f"• Summary: {body[:150]}...\n"
                )

            # 2. Package the Proactive Report
            report_payload = {
                "report_id": f"rep-{int(time.time())}-{email_id}",
                "email_id": email_id,
                "sender": sender,
                "subject": subject,
                "priority": priority,
                "briefing": briefing_text.strip(),
                "timestamp": email.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S UTC")),
                "type": "PROACTIVE_CEO_EMAIL_ALERT",
            }

            # 3. Proactively broadcast to CEO via WebSockets & Notification Channel
            try:
                await ws_hub.broadcast_to_channel(
                    channel="ceo_alerts",
                    message={
                        "event": "PROACTIVE_EMAIL_REPORT",
                        "data": report_payload,
                    },
                )
                await ws_hub.broadcast_to_channel(
                    channel="system_notifications",
                    message={
                        "event": "EXECUTIVE_ALERT",
                        "text": f"📩 Proactive Briefing: {subject}",
                        "priority": priority,
                    },
                )
                logger.info(f"📢 [Proactive Email Report Dispatched] -> CEO Alert for email '{subject}'")
            except Exception as e:
                logger.error(f"Failed to broadcast CEO alert: {e}")

            # 4. Mark as reported so we never duplicate
            await mark_email_reported(email_id)
            generated_reports.append(report_payload)
            self._recent_reports.append(report_payload)

            if len(self._recent_reports) > 50:
                self._recent_reports = self._recent_reports[-50:]

        return generated_reports

    def get_recent_reports(self) -> list[dict[str, Any]]:
        return list(self._recent_reports)


# Global singleton instance
email_agent = EmailIntelligenceAgent(check_interval_seconds=30)
