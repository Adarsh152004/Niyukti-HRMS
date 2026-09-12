"""
Autonomous Gmail Tools for HRMS AI Agents.
Provides agent tool declarations and execution handlers for real Gmail interactions.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List, Optional
from backend.integrations.gmail_client import gmail_client

async def tool_send_gmail(to_email: str, subject: str, body: str) -> Dict[str, Any]:
    """Agent tool to send an email via real Gmail API."""
    if not gmail_client.is_configured():
        return {
            "success": False,
            "error": "Gmail OAuth credentials are not configured in backend environment."
        }
    try:
        res = await gmail_client.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            is_html=False
        )
        return {
            "success": True,
            "message_id": res.get("message_id"),
            "to": to_email,
            "subject": subject,
            "detail": f"Email successfully dispatched to {to_email}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def tool_list_gmail_messages(query: str = "label:INBOX", max_results: int = 5) -> Dict[str, Any]:
    """Agent tool to list recent or unread emails from Gmail inbox."""
    if not gmail_client.is_configured():
        return {
            "success": False,
            "error": "Gmail OAuth credentials are not configured in backend environment."
        }
    try:
        msgs = await gmail_client.list_messages(query=query, max_results=max_results)
        return {
            "success": True,
            "count": len(msgs),
            "messages": msgs
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
