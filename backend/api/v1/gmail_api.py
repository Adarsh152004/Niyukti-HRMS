"""
API v1 — Real Google Gmail Integration Endpoints (`/api/v1/gmail`).
Provides live connection diagnostics, email inbox querying, and real email dispatch.
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field

from backend.integrations.gmail_client import gmail_client

router = APIRouter(prefix="/gmail", tags=["Gmail Integration"])


class SendEmailRequest(BaseModel):
    to_email: str = Field(..., example="candidate@domain.com")
    subject: str = Field(..., example="Welcome to Azyntrix - Offer Letter & Onboarding")
    body: str = Field(..., example="Dear Candidate, we are thrilled to extend this offer...")
    is_html: bool = Field(default=False)
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None


class TestEmailRequest(BaseModel):
    to_email: str = Field(..., example="adarshyt1504@gmail.com")


@router.get("/status")
async def get_gmail_status() -> Dict[str, Any]:
    """Check live Gmail API OAuth2 connection and mailbox stats."""
    if not gmail_client.is_configured():
        return {
            "status": "unconfigured",
            "connected": False,
            "message": "Gmail OAuth credentials are not set in environment."
        }
    try:
        res = await gmail_client.verify_connection()
        return {
            "status": "connected" if res.get("connected") else "error",
            "sender_email": gmail_client.sender_email,
            **res
        }
    except Exception as e:
        return {
            "status": "error",
            "connected": False,
            "error": str(e)
        }


@router.get("/messages")
async def list_gmail_messages(
    query: str = Query(default="", description="Gmail search filter"),
    max_results: int = Query(default=10, ge=1, le=50)
) -> List[Dict[str, Any]]:
    """List recent messages matching a query from Gmail inbox."""
    try:
        return await gmail_client.list_messages(query=query, max_results=max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list Gmail messages: {str(e)}")


@router.get("/messages/{message_id}")
async def get_gmail_message(message_id: str) -> Dict[str, Any]:
    """Retrieve full details and snippet for a specific email."""
    try:
        return await gmail_client.get_message(message_id=message_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Message not found: {str(e)}")


@router.post("/send")
async def send_gmail_email(req: SendEmailRequest) -> Dict[str, Any]:
    """Send an email through the authenticated Gmail account."""
    try:
        result = await gmail_client.send_email(
            to_email=req.to_email,
            subject=req.subject,
            body=req.body,
            is_html=req.is_html,
            cc=req.cc,
            bcc=req.bcc
        )
        return {
            "status": "success",
            "data": result,
            "message": f"Email successfully dispatched to {req.to_email}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
