"""
Gmail MCP Server & HRMS Real Email Intelligence Tools.

Provides production email capabilities for HRMS agents:
- Search and query real Google Gmail / Workspace messages and threads
- Fetch and parse real email message content and metadata
- Compose and dispatch RFC 2822 compliant emails via Gmail API or Gmail MCP Server
- Ingest and flag priority unread emails for autonomous CEO reporting
- Automatic OAuth2 token refreshing using client credentials
"""

from __future__ import annotations

import asyncio
import base64
import email
from email.mime.text import MIMEText
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


class RealGmailOAuthProvider(GmailProvider):
    """
    Production Google Gmail Provider using direct Google Workspace REST API
    and OAuth2 refresh token flows.
    """

    def __init__(self):
        self.api_url = os.getenv("GMAIL_API_URL", "https://gmail.googleapis.com/gmail/v1/users/me").rstrip("/")
        self.mcp_url = os.getenv("GMAIL_MCP_URL", "").rstrip("/")
        self.client_id = os.getenv("GMAIL_CLIENT_ID", "")
        self.client_secret = os.getenv("GMAIL_CLIENT_SECRET", "")
        self.refresh_token = os.getenv("GMAIL_REFRESH_TOKEN", "")
        self.access_token = os.getenv("GMAIL_ACCESS_TOKEN", "")
        self.token_expiry: float = 0.0
        self.reported_ids: set[str] = set()

    async def _ensure_access_token(self) -> str:
        """Returns valid access token or refreshes it via Google OAuth2."""
        now = time.time()
        if self.access_token and now < self.token_expiry:
            return self.access_token

        client_id = self.client_id or os.getenv("GMAIL_CLIENT_ID", "")
        client_secret = self.client_secret or os.getenv("GMAIL_CLIENT_SECRET", "")
        refresh_token = self.refresh_token or os.getenv("GMAIL_REFRESH_TOKEN", "")

        if refresh_token and client_id and client_secret:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        "https://oauth2.googleapis.com/token",
                        data={
                            "client_id": client_id,
                            "client_secret": client_secret,
                            "refresh_token": refresh_token,
                            "grant_type": "refresh_token",
                        },
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        self.access_token = data.get("access_token", "")
                        expires_in = data.get("expires_in", 3600)
                        self.token_expiry = now + expires_in - 120
                        logger.info("Successfully refreshed Google Gmail OAuth2 access token.")
                        return self.access_token
                    else:
                        logger.warning(f"Failed to refresh Google OAuth token: {resp.status_code} {resp.text}")
            except Exception as e:
                logger.error(f"Error during OAuth refresh: {e}")

        return self.access_token

    def _auth_headers(self, token: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def search_messages(self, query: str, max_results: int = 10) -> list[GmailMessage]:
        token = await self._ensure_access_token()
        if not token:
            logger.info("Gmail OAuth credentials not configured. Please set GMAIL_CLIENT_ID & GMAIL_REFRESH_TOKEN.")
            return []

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                params = {"maxResults": max_results}
                if query.strip():
                    params["q"] = query.strip()
                
                resp = await client.get(
                    f"{self.api_url}/messages",
                    headers=self._auth_headers(token),
                    params=params,
                )
                if resp.status_code == 200:
                    items = resp.json().get("messages", [])
                    results: list[GmailMessage] = []
                    for item in items:
                        msg = await self.get_message(item["id"])
                        if msg:
                            results.append(msg)
                    return results
                else:
                    logger.error(f"Gmail API search failed: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"Gmail search exception: {e}")
        return []

    async def get_message(self, message_id: str) -> GmailMessage | None:
        token = await self._ensure_access_token()
        if not token:
            return None

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{self.api_url}/messages/{message_id}?format=full",
                    headers=self._auth_headers(token),
                )
                if resp.status_code == 200:
                    data = resp.json()
                    payload = data.get("payload", {})
                    headers_list = payload.get("headers", [])
                    headers = {h["name"].lower(): h["value"] for h in headers_list}

                    snippet = data.get("snippet", "")
                    labels = data.get("labelIds", [])
                    is_unread = "UNREAD" in labels
                    
                    # Extract body text
                    body_text = snippet
                    parts = payload.get("parts", [])
                    if parts:
                        for part in parts:
                            if part.get("mimeType") == "text/plain":
                                data_bytes = part.get("body", {}).get("data", "")
                                if data_bytes:
                                    try:
                                        body_text = base64.urlsafe_b64decode(data_bytes + "==").decode("utf-8", errors="replace")
                                    except Exception:
                                        pass
                                break

                    # Assess priority
                    subject = headers.get("subject", "No Subject")
                    priority = "NORMAL"
                    if "urgent" in subject.lower() or "critical" in subject.lower() or "offer" in subject.lower():
                        priority = "CRITICAL"
                    elif "IMPORTANT" in labels:
                        priority = "HIGH"

                    return GmailMessage(
                        id=data["id"],
                        thread_id=data.get("threadId", ""),
                        sender=headers.get("from", "unknown"),
                        recipient=headers.get("to", "unknown"),
                        subject=subject,
                        body=body_text,
                        snippet=snippet,
                        timestamp=headers.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")),
                        is_unread=is_unread,
                        labels=labels,
                        priority_level=priority,
                    )
        except Exception as e:
            logger.error(f"Gmail get_message exception for {message_id}: {e}")
        return None

    async def send_message(self, to: str, subject: str, body: str, cc: list[str] | None = None) -> GmailSendResult:
        token = await self._ensure_access_token()
        if not token:
            return GmailSendResult(
                success=False,
                error="Gmail credentials not configured. Please set GMAIL_CLIENT_ID and GMAIL_REFRESH_TOKEN in .env"
            )

        try:
            mime_msg = MIMEText(body)
            mime_msg["to"] = to
            mime_msg["subject"] = subject
            if cc:
                mime_msg["cc"] = ", ".join(cc)

            raw_bytes = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode("utf-8")

            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.api_url}/messages/send",
                    headers=self._auth_headers(token),
                    json={"raw": raw_bytes},
                )
                if resp.status_code == 200:
                    res_data = resp.json()
                    now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    return GmailSendResult(
                        success=True,
                        message_id=res_data.get("id", ""),
                        thread_id=res_data.get("threadId", ""),
                        timestamp=now_ts,
                    )
                else:
                    return GmailSendResult(success=False, error=f"Gmail API Error: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"Error sending email via Gmail API: {e}")
            return GmailSendResult(success=False, error=str(e))

    async def get_unread_important(self) -> list[GmailMessage]:
        return await self.search_messages("is:unread", max_results=5)

    async def mark_reported(self, message_id: str) -> bool:
        self.reported_ids.add(message_id)
        token = await self._ensure_access_token()
        if token:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(
                        f"{self.api_url}/messages/{message_id}/modify",
                        headers=self._auth_headers(token),
                        json={"removeLabelIds": ["UNREAD"]},
                    )
            except Exception as e:
                logger.warning(f"Could not mark unread on Gmail API: {e}")
        return True

    async def get_status(self) -> dict[str, Any]:
        token = await self._ensure_access_token()
        return {
            "provider": "google_workspace_gmail_real",
            "status": "AUTHENTICATED" if token else "CREDENTIALS_REQUIRED",
            "endpoint": self.api_url,
            "has_refresh_token": bool(self.refresh_token),
            "reported_count": len(self.reported_ids),
        }


# Singleton Gmail Provider Instance
_provider_instance: GmailProvider | None = None


def get_gmail_provider() -> GmailProvider:
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = RealGmailOAuthProvider()
    return _provider_instance


# ---------------------------------------------------------------------------
# High-Level Agent Tool Functions (Bound into Multi-Agent Tool Catalogs)
# ---------------------------------------------------------------------------

async def search_emails(query: str = "", max_results: int = 5) -> str:
    """
    Search Gmail messages by keywords, sender, labels, or subject.
    """
    provider = get_gmail_provider()
    msgs = await provider.search_messages(query=query, max_results=max_results)
    if not msgs:
        status = await provider.get_status()
        if status.get("status") == "CREDENTIALS_REQUIRED":
            return (
                "⚠️ Real Gmail integration is enabled, but credentials are not yet configured in .env.\n"
                "Please configure GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, and GMAIL_REFRESH_TOKEN.\n"
                "Refer to docs/GMAIL_MCP_SETUP_GUIDE.md for step-by-step instructions."
            )
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
    """
    provider = get_gmail_provider()
    msg = await provider.get_message(message_id=message_id)
    if not msg:
        return f"Email message ID '{message_id}' not found on server."

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
    """
    provider = get_gmail_provider()
    cc_list = [c.strip() for c in cc.split(",") if c.strip()] if cc else None
    result = await provider.send_message(to=to, subject=subject, body=body, cc=cc_list)
    if result.success:
        return (
            f"✅ Email successfully dispatched via Gmail API!\n"
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
