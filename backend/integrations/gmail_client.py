"""
Real Google Gmail Integration Client via Google OAuth2 REST API.
Handles:
- Automatic token refresh using client_id, client_secret, and refresh_token
- Listing inbox/unread messages
- Reading message details (subject, from, to, snippet, body)
- Sending RFC 2822 emails (HTML and Plaintext) via Gmail API
"""

from __future__ import annotations
import os
import base64
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
import httpx
import logging

logger = logging.getLogger("hrms.integrations.gmail")

class GmailClient:
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        refresh_token: Optional[str] = None,
        sender_email: Optional[str] = None,
    ):
        self.client_id = client_id or os.getenv("GMAIL_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("GMAIL_CLIENT_SECRET", "")
        self.refresh_token = refresh_token or os.getenv("GMAIL_REFRESH_TOKEN", "")
        self.sender_email = sender_email or os.getenv("GMAIL_SENDER_EMAIL", "me")
        self._access_token: Optional[str] = None

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret and self.refresh_token)

    async def get_access_token(self) -> str:
        """Exchange refresh token for a fresh Google OAuth2 access token."""
        if not self.is_configured():
            raise ValueError("Gmail OAuth credentials (client_id, client_secret, refresh_token) are not configured.")

        url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, data=payload)
            if resp.status_code != 200:
                logger.error(f"Failed to refresh Gmail access token: {resp.text}")
                raise RuntimeError(f"Google OAuth Token Refresh Failed ({resp.status_code}): {resp.text}")
            
            data = resp.json()
            self._access_token = data.get("access_token")
            return self._access_token

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Send an email using the Gmail REST API (users.messages.send)."""
        token = await self.get_access_token()

        message = MIMEMultipart("alternative")
        message["to"] = to_email
        message["from"] = self.sender_email
        message["subject"] = subject

        if cc:
            message["cc"] = ", ".join(cc)
        if bcc:
            message["bcc"] = ", ".join(bcc)

        mime_part = MIMEText(body, "html" if is_html else "plain", "utf-8")
        message.attach(mime_part)

        raw_bytes = message.as_bytes()
        raw_b64 = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")

        send_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(send_url, headers=headers, json={"raw": raw_b64})
            if resp.status_code not in (200, 201):
                logger.error(f"Gmail send failed: {resp.text}")
                raise RuntimeError(f"Gmail API send failed ({resp.status_code}): {resp.text}")
            
            result = resp.json()
            logger.info(f"Email sent successfully via Gmail API. ID: {result.get('id')}")
            return {
                "status": "sent",
                "message_id": result.get("id"),
                "thread_id": result.get("threadId"),
                "to": to_email,
                "subject": subject,
            }

    async def list_messages(self, query: str = "", max_results: int = 10) -> List[Dict[str, Any]]:
        """List messages in inbox matching query."""
        token = await self.get_access_token()
        q_param = f"&q={query}" if query else ""
        list_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults={max_results}{q_param}"
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(list_url, headers=headers)
            if resp.status_code != 200:
                logger.error(f"Gmail list messages failed: {resp.text}")
                raise RuntimeError(f"Gmail list messages failed: {resp.text}")
            
            data = resp.json()
            raw_msgs = data.get("messages", [])
            
            results = []
            for m in raw_msgs[:max_results]:
                msg_id = m.get("id")
                try:
                    detail = await self.get_message(msg_id)
                    results.append(detail)
                except Exception as e:
                    logger.warning(f"Failed to fetch detail for message {msg_id}: {e}")
                    results.append({"id": msg_id, "thread_id": m.get("threadId")})
            
            return results

    async def get_message(self, message_id: str) -> Dict[str, Any]:
        """Fetch details of a specific message by ID."""
        token = await self.get_access_token()
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}?format=full"
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(f"Failed to fetch message {message_id}: {resp.text}")
            
            data = resp.json()
            payload = data.get("payload", {})
            headers_list = payload.get("headers", [])

            headers_map = {h["name"].lower(): h["value"] for h in headers_list}
            subject = headers_map.get("subject", "(No Subject)")
            sender = headers_map.get("from", "(Unknown)")
            recipient = headers_map.get("to", "(Unknown)")
            date = headers_map.get("date", "")
            snippet = data.get("snippet", "")

            # Extract body snippet
            body_text = snippet
            return {
                "id": message_id,
                "thread_id": data.get("threadId"),
                "subject": subject,
                "from": sender,
                "to": recipient,
                "date": date,
                "snippet": snippet,
                "label_ids": data.get("labelIds", []),
            }

    async def verify_connection(self) -> Dict[str, Any]:
        """Check connection by getting user profile or refreshing token."""
        token = await self.get_access_token()
        url = "https://gmail.googleapis.com/gmail/v1/users/me/profile"
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                profile = resp.json()
                return {
                    "connected": True,
                    "email_address": profile.get("emailAddress", self.sender_email),
                    "messages_total": profile.get("messagesTotal", 0),
                    "threads_total": profile.get("threadsTotal", 0),
                }
            return {
                "connected": False,
                "error": f"HTTP {resp.status_code}: {resp.text}"
            }

# Global singleton instance
gmail_client = GmailClient()
