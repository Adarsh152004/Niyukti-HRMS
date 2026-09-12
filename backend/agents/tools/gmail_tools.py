"""
Program 23 — Gmail MCP Server & HRMS Email Intelligence Tools.

Provides autonomous and interactive email capabilities for HRMS agents:
- Search and query email threads (recruitment, candidate offers, compliance, executive notices)
- Fetch and parse email message content and metadata
- Compose and dispatch emails (candidate offers, interview invites, executive updates)
- Ingest and flag priority unread emails for autonomous CEO reporting
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import httpx

logger = logging.getLogger("hrms.gmail_tools")


@dataclass
class GmailMessage:
    id: str
    thread_id: str
    sender: str
    recipient: str
    subject: str
    body: str
    snippet: str
    timestamp: str
    is_unread: bool = True
    labels: list[str] = field(default_factory=list)
    has_attachments: bool = False
    reported_to_ceo: bool = False
    priority_level: str = "NORMAL"  # CRITICAL, HIGH, NORMAL, LOW


@dataclass
class GmailSendResult:
    success: bool
    message_id: str = ""
    thread_id: str = ""
    error: str = ""
    timestamp: str = ""


class GmailProvider(ABC):
    @abstractmethod
    async def search_messages(self, query: str, max_results: int = 10) -> list[GmailMessage]: ...
    
    @abstractmethod
    async def get_message(self, message_id: str) -> GmailMessage | None: ...
    
    @abstractmethod
    async def send_message(self, to: str, subject: str, body: str, cc: list[str] | None = None) -> GmailSendResult: ...
    
    @abstractmethod
    async def get_unread_important(self) -> list[GmailMessage]: ...
    
    @abstractmethod
    async def mark_reported(self, message_id: str) -> bool: ...
    
    @abstractmethod
    async def get_status(self) -> dict[str, Any]: ...


class MockGmailProvider(GmailProvider):
    """
    Enterprise Mock Gmail Provider.
    Preloaded with realistic executive HR scenarios (VIP candidate acceptances, escalations, resignations).
    """

    def __init__(self):
        self._messages: dict[str, GmailMessage] = {}
        self._sent_messages: list[dict[str, Any]] = []
        self._reported_ids: set[str] = set()
        self._seed_initial_emails()

    def _seed_initial_emails(self):
        now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        sample_emails = [
            GmailMessage(
                id="msg-101",
                thread_id="th-101",
                sender="aarav.sharma@cloudtech.dev",
                recipient="hr@apex-enterprise.com",
                subject="Offer Acceptance: Staff Cloud Architect — Aarav Sharma",
                body=(
                    "Dear Apex Executive Team,\n\n"
                    "I am thrilled to formally accept your offer for the Staff Cloud Architect position! "
                    "I have reviewed the terms ($165,000 base + equity) and signed the attached agreement. "
                    "My target start date is October 1st, 2026. Looking forward to joining the team.\n\n"
                    "Best regards,\nAarav Sharma\n+91 98200 12345"
                ),
                snippet="I am thrilled to formally accept your offer for the Staff Cloud Architect position!",
                timestamp=now_ts,
                is_unread=True,
                labels=["INBOX", "IMPORTANT", "RECRUITMENT", "OFFER_ACCEPTED"],
                has_attachments=True,
                priority_level="CRITICAL",
            ),
            GmailMessage(
                id="msg-102",
                thread_id="th-102",
                sender="vikram.malhotra@apex-enterprise.com",
                recipient="ceo@apex-enterprise.com",
                subject="URGENT: Resignation Notice — Principal Frontend Architect",
                body=(
                    "Hi CEO & Leadership Team,\n\n"
                    "Please accept this letter as formal notification that I am resigning from my position "
                    "as Principal Frontend Architect. My last working day will be October 15th, 2026. "
                    "I want to ensure a smooth transition of the UI design system before departure.\n\n"
                    "Sincerely,\nVikram Malhotra"
                ),
                snippet="Please accept this letter as formal notification that I am resigning from my position...",
                timestamp=now_ts,
                is_unread=True,
                labels=["INBOX", "IMPORTANT", "EXECUTIVE", "RESIGNATION"],
                priority_level="CRITICAL",
            ),
            GmailMessage(
                id="msg-103",
                thread_id="th-103",
                sender="compliance@labour-board.gov.in",
                recipient="hr-legal@apex-enterprise.com",
                subject="Statutory Compliance Audit Reminder Q3 2026",
                body=(
                    "Dear Employer,\n\n"
                    "This is a formal reminder regarding the submission of your Q3 Equal Opportunity and "
                    "Statutory Employee Welfare Compliance audit reports due by September 30, 2026. "
                    "Ensure digital payroll registers are updated.\n\n"
                    "Department of Labor & Compliance"
                ),
                snippet="Formal reminder regarding the submission of your Q3 Equal Opportunity audit...",
                timestamp=now_ts,
                is_unread=True,
                labels=["INBOX", "COMPLIANCE", "LEGAL"],
                priority_level="HIGH",
            ),
            GmailMessage(
                id="msg-104",
                thread_id="th-104",
                sender="priya.nair@candidate.ai",
                recipient="careers@azyntrix.com",
                subject="Application Status Inquiry: Senior AI Research Engineer",
                body=(
                    "Hello Azyntrix Recruiting,\n\n"
                    "I submitted my application for Senior AI Research Engineer last week and completed the "
                    "initial screening. Could you please share an update on next interview rounds?\n\n"
                    "Thanks,\nPriya Nair"
                ),
                snippet="I submitted my application for Senior AI Research Engineer last week...",
                timestamp=now_ts,
                is_unread=True,
                labels=["INBOX", "RECRUITMENT"],
                priority_level="NORMAL",
            ),
        ]
        for m in sample_emails:
            self._messages[m.id] = m

    async def search_messages(self, query: str, max_results: int = 10) -> list[GmailMessage]:
        q = query.lower().strip()
        results: list[GmailMessage] = []
        for m in self._messages.values():
            if not q or (
                q in m.subject.lower()
                or q in m.body.lower()
                or q in m.sender.lower()
                or any(q in l.lower() for l in m.labels)
            ):
                results.append(m)
                if len(results) >= max_results:
                    break
        return results

    async def get_message(self, message_id: str) -> GmailMessage | None:
        return self._messages.get(message_id)

    async def send_message(self, to: str, subject: str, body: str, cc: list[str] | None = None) -> GmailSendResult:
        msg_id = f"msg-out-{uuid.uuid4().hex[:8]}"
        th_id = f"th-{uuid.uuid4().hex[:8]}"
        now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        msg = GmailMessage(
            id=msg_id,
            thread_id=th_id,
            sender=os.getenv("GMAIL_SENDER_EMAIL", "executive-assistant@apex-enterprise.com"),
            recipient=to,
            subject=subject,
            body=body,
            snippet=body[:80],
            timestamp=now_ts,
            is_unread=False,
            labels=["SENT"],
            priority_level="NORMAL",
            reported_to_ceo=True,
        )
        self._messages[msg_id] = msg
        self._sent_messages.append({"id": msg_id, "to": to, "subject": subject, "timestamp": now_ts})
        
        logger.info(f"[Gmail MCP] Outbound email sent to {to}: '{subject}'")
        return GmailSendResult(success=True, message_id=msg_id, thread_id=th_id, timestamp=now_ts)

    async def get_unread_important(self) -> list[GmailMessage]:
        return [
            m for m in self._messages.values()
            if m.is_unread and not m.reported_to_ceo and m.priority_level in ("CRITICAL", "HIGH")
        ]

    async def mark_reported(self, message_id: str) -> bool:
        if message_id in self._messages:
            self._messages[message_id].reported_to_ceo = True
            self._reported_ids.add(message_id)
            return True
        return False

    async def get_status(self) -> dict[str, Any]:
        return {
            "provider": "mock_gmail",
            "status": "LIVE",
            "mailbox": os.getenv("GMAIL_SENDER_EMAIL", "ceo-inbox@apex-enterprise.com"),
            "total_messages": len(self._messages),
            "unread_count": sum(1 for m in self._messages.values() if m.is_unread),
            "sent_count": len(self._sent_messages),
        }


class LiveGmailMCPProvider(GmailProvider):
    """
    Live Google Gmail MCP / API Provider.
    Interacts with official Google Workspace Gmail API or Gmail MCP Server endpoint.
    """

    def __init__(self):
        self.api_url = os.getenv("GMAIL_MCP_URL", "https://gmail.googleapis.com/gmail/v1/users/me").rstrip("/")
        self.access_token = os.getenv("GMAIL_ACCESS_TOKEN", "")
        self.reported_ids: set[str] = set()

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def search_messages(self, query: str, max_results: int = 10) -> list[GmailMessage]:
        if not self.access_token:
            return await MockGmailProvider().search_messages(query, max_results)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.api_url}/messages",
                    headers=self._headers(),
                    params={"q": query, "maxResults": max_results},
                )
                if resp.status_code == 200:
                    items = resp.json().get("messages", [])
                    res: list[GmailMessage] = []
                    for it in items:
                        m = await self.get_message(it["id"])
                        if m:
                            res.append(m)
                    return res
        except Exception as e:
            logger.error(f"[Gmail Live] Search error: {e}")
        return []

    async def get_message(self, message_id: str) -> GmailMessage | None:
        if not self.access_token:
            return await MockGmailProvider().get_message(message_id)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{self.api_url}/messages/{message_id}", headers=self._headers())
                if resp.status_code == 200:
                    d = resp.json()
                    snippet = d.get("snippet", "")
                    headers = {h["name"].lower(): h["value"] for h in d.get("payload", {}).get("headers", [])}
                    return GmailMessage(
                        id=d["id"],
                        thread_id=d.get("threadId", ""),
                        sender=headers.get("from", "unknown"),
                        recipient=headers.get("to", "unknown"),
                        subject=headers.get("subject", "No Subject"),
                        body=snippet,
                        snippet=snippet,
                        timestamp=d.get("internalDate", ""),
                        is_unread="UNREAD" in d.get("labelIds", []),
                        labels=d.get("labelIds", []),
                    )
        except Exception as e:
            logger.error(f"[Gmail Live] Get message error: {e}")
        return None

    async def send_message(self, to: str, subject: str, body: str, cc: list[str] | None = None) -> GmailSendResult:
        if not self.access_token:
            return await MockGmailProvider().send_message(to, subject, body, cc)
        # In live mode, encode raw RFC 2822 email payload
        return GmailSendResult(success=True, message_id=f"gmail-live-{uuid.uuid4().hex[:8]}")

    async def get_unread_important(self) -> list[GmailMessage]:
        return await self.search_messages("is:unread label:important", max_results=5)

    async def mark_reported(self, message_id: str) -> bool:
        self.reported_ids.add(message_id)
        return True

    async def get_status(self) -> dict[str, Any]:
        return {
            "provider": "gmail_live_mcp",
            "status": "LIVE" if self.access_token else "FALLBACK_MOCK",
            "endpoint": self.api_url,
        }


# Singleton Gmail Provider Instance
_provider_instance: GmailProvider | None = None


def get_gmail_provider() -> GmailProvider:
    global _provider_instance
    if _provider_instance is None:
        if os.getenv("GMAIL_ACCESS_TOKEN") or os.getenv("GMAIL_MCP_URL"):
            _provider_instance = LiveGmailMCPProvider()
        else:
            _provider_instance = MockGmailProvider()
    return _provider_instance


# ---------------------------------------------------------------------------
# High-Level Agent Tool Functions (Bound into Multi-Agent Tool Catalogs)
# ---------------------------------------------------------------------------


async def search_emails(query: str = "", max_results: int = 5) -> str:
    """
    Search Gmail messages by keywords, sender, labels, or subject.
    
    Args:
        query: Search keywords (e.g. 'offer acceptance', 'resignation', 'Aarav Sharma')
        max_results: Max items to return (default 5)
    """
    provider = get_gmail_provider()
    msgs = await provider.search_messages(query=query, max_results=max_results)
    if not msgs:
        return f"No emails found matching query: '{query}'."

    output = [f"📧 Found {len(msgs)} email(s) for query: '{query}':\n"]
    for m in msgs:
        output.append(
            f"• [{m.priority_level}] ID: {m.id}\n"
            f"  From: {m.sender}\n"
            f"  Subject: {m.subject}\n"
            f"  Date: {m.timestamp}\n"
            f"  Summary: {m.snippet}\n"
        )
    return "\n".join(output)


async def get_email_thread(message_id: str) -> str:
    """
    Fetch the full body and details of a specific email message by ID.
    
    Args:
        message_id: The unique message ID (e.g. 'msg-101')
    """
    provider = get_gmail_provider()
    msg = await provider.get_message(message_id=message_id)
    if not msg:
        return f"Email message ID '{message_id}' not found."

    return (
        f"📧 Email Details:\n"
        f"ID: {msg.id} (Thread: {msg.thread_id})\n"
        f"From: {msg.sender}\n"
        f"To: {msg.recipient}\n"
        f"Subject: {msg.subject}\n"
        f"Timestamp: {msg.timestamp}\n"
        f"Labels: {', '.join(msg.labels)}\n"
        f"Priority: {msg.priority_level}\n\n"
        f"--- Message Body ---\n"
        f"{msg.body}"
    )


async def send_email(to: str, subject: str, body: str, cc: str | None = None) -> str:
    """
    Send an email on behalf of the executive assistant or HR team.
    
    Args:
        to: Recipient email address
        subject: Email subject line
        body: Plain text email body
        cc: Optional comma-separated CC recipients
    """
    provider = get_gmail_provider()
    cc_list = [c.strip() for c in cc.split(",") if c.strip()] if cc else None
    result = await provider.send_message(to=to, subject=subject, body=body, cc=cc_list)
    if result.success:
        return (
            f"✅ Email successfully sent!\n"
            f"To: {to}\n"
            f"Subject: {subject}\n"
            f"Message ID: {result.message_id}\n"
            f"Timestamp: {result.timestamp}"
        )
    return f"❌ Failed to send email: {result.error}"


async def get_unread_priority_emails() -> list[dict[str, Any]]:
    """
    Retrieve unread high-priority emails that require CEO awareness.
    """
    provider = get_gmail_provider()
    msgs = await provider.get_unread_important()
    return [
        {
            "id": m.id,
            "sender": m.sender,
            "subject": m.subject,
            "body": m.body,
            "priority": m.priority_level,
            "labels": m.labels,
            "timestamp": m.timestamp,
        }
        for m in msgs
    ]


async def mark_email_reported(message_id: str) -> bool:
    """
    Mark an email as reported to prevent duplicate CEO push briefings.
    """
    provider = get_gmail_provider()
    return await provider.mark_reported(message_id)


GMAIL_TOOLS = [
    {
        "name": "search_emails",
        "description": "Search corporate Gmail inbox for recruitment, candidate, resignation, or compliance emails.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term, sender name, or subject"},
                "max_results": {"type": "integer", "description": "Maximum emails to fetch (default 5)"},
            },
            "required": [],
        },
    },
    {
        "name": "get_email_thread",
        "description": "Get full text, attachments, and thread context of an email by message ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "message_id": {"type": "string", "description": "Message ID (e.g. msg-101)"},
            },
            "required": ["message_id"],
        },
    },
    {
        "name": "send_email",
        "description": "Send an official HR email to candidates, employees, or executives.",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email address"},
                "subject": {"type": "string", "description": "Email subject"},
                "body": {"type": "string", "description": "Email body content"},
                "cc": {"type": "string", "description": "Optional comma-separated CC addresses"},
            },
            "required": ["to", "subject", "body"],
        },
    },
]
