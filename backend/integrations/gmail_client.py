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
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._sender_email = sender_email
        self._access_token: Optional[str] = None

    @property
    def client_id(self) -> str:
        return self._client_id or os.getenv("GMAIL_CLIENT_ID", "")

    @property
    def client_secret(self) -> str:
        return self._client_secret or os.getenv("GMAIL_CLIENT_SECRET", "")

    @property
    def refresh_token(self) -> str:
        return self._refresh_token or os.getenv("GMAIL_REFRESH_TOKEN", "")

    @property
    def sender_email(self) -> str:
        return self._sender_email or os.getenv("GMAIL_SENDER_EMAIL", "2000nyrasharma@gmail.com")

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

    def build_interview_invite_html(
        self,
        candidate_name: str,
        role: str,
        date_time: str,
        meet_link: str = "https://meet.google.com/azy-hrms-int",
        interviewer: str = "Talent Acquisition & Engineering Panel"
    ) -> str:
        """Generate high-impact branded HTML email for Stage 1: Interview Invite."""
        return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; color: #1e293b; }}
    .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
    .header {{ background: linear-gradient(135deg, #0ea5e9, #2563eb); padding: 30px; text-align: center; color: #ffffff; }}
    .content {{ padding: 30px; line-height: 1.6; }}
    .card {{ background: #f1f5f9; border-left: 4px solid #0284c7; padding: 16px; border-radius: 6px; margin: 20px 0; }}
    .btn {{ display: inline-block; background: #0284c7; color: #ffffff !important; padding: 12px 28px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 15px 0; }}
    .footer {{ background: #f8fafc; padding: 20px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1 style="margin: 0; font-size: 24px; letter-spacing: -0.5px;">Azyntrix Talent Acquisition</h1>
      <p style="margin: 6px 0 0 0; opacity: 0.9; font-size: 14px;">Stage 1: Interview Invitation</p>
    </div>
    <div class="content">
      <p>Dear <strong>{candidate_name}</strong>,</p>
      <p>Thank you for your interest in joining <strong>Azyntrix Technologies</strong>. Following our review of your profile, we are pleased to invite you for a technical and culture interview for the position of <strong>{role}</strong>.</p>
      
      <div class="card">
        <h3 style="margin: 0 0 10px 0; color: #0369a1; font-size: 16px;">📅 Interview Details</h3>
        <p style="margin: 4px 0;"><strong>Role:</strong> {role}</p>
        <p style="margin: 4px 0;"><strong>Scheduled Time:</strong> {date_time}</p>
        <p style="margin: 4px 0;"><strong>Panel:</strong> {interviewer}</p>
        <p style="margin: 4px 0;"><strong>Platform:</strong> Google Meet / Virtual Room</p>
      </div>

      <div style="text-align: center;">
        <a href="{meet_link}" class="btn" target="_blank">Join Google Meet Interview</a>
      </div>

      <p style="font-size: 14px; color: #475569;">Please ensure you are in a quiet environment with a stable internet connection. If you need to reschedule, reply directly to this email at least 24 hours in advance.</p>
      
      <p>Best regards,<br><strong>People & Talent Operations Team</strong><br>Azyntrix Intelligence HRMS</p>
    </div>
    <div class="footer">
      <p style="margin: 0;">© 2026 Azyntrix Technologies Inc. All rights reserved.<br>This is an automated communication dispatched via Azyntrix HR Intelligence OS.</p>
    </div>
  </div>
</body>
</html>
"""

    def build_evaluation_feedback_html(
        self,
        candidate_name: str,
        role: str,
        status: str = "RECOMMENDED_FOR_OFFER",
        score: str = "94/100",
        feedback_summary: str = "Demonstrated exceptional system design, backend mastery, and cultural alignment."
    ) -> str:
        """Generate high-impact branded HTML email for Stage 2: Evaluation Feedback."""
        badge_color = "#10b981" if "RECOMMEND" in status.upper() or "PASS" in status.upper() else "#f59e0b"
        return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; color: #1e293b; }}
    .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
    .header {{ background: linear-gradient(135deg, #6366f1, #4f46e5); padding: 30px; text-align: center; color: #ffffff; }}
    .content {{ padding: 30px; line-height: 1.6; }}
    .card {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 18px; border-radius: 8px; margin: 20px 0; }}
    .badge {{ display: inline-block; background: {badge_color}; color: #ffffff; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 13px; }}
    .footer {{ background: #f8fafc; padding: 20px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1 style="margin: 0; font-size: 24px; letter-spacing: -0.5px;">Azyntrix Technical Review</h1>
      <p style="margin: 6px 0 0 0; opacity: 0.9; font-size: 14px;">Stage 2: Evaluation & Assessment Scorecard</p>
    </div>
    <div class="content">
      <p>Dear <strong>{candidate_name}</strong>,</p>
      <p>Thank you for completing your evaluation rounds for the <strong>{role}</strong> position at Azyntrix.</p>
      
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <h3 style="margin: 0; color: #1e293b; font-size: 16px;">Assessment Summary</h3>
          <span class="badge">{status.replace('_', ' ')}</span>
        </div>
        <p style="margin: 4px 0;"><strong>Overall Score:</strong> <span style="color: #4f46e5; font-weight: 700;">{score}</span></p>
        <p style="margin: 4px 0;"><strong>Evaluated Role:</strong> {role}</p>
        <p style="margin: 10px 0 4px 0;"><strong>Panel Feedback:</strong></p>
        <p style="margin: 0; color: #475569; font-style: italic; background: #ffffff; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;">"{feedback_summary}"</p>
      </div>

      <p>Our executive hiring committee has reviewed your score and is finalizing the official employment proposal.</p>
      
      <p>Best regards,<br><strong>Engineering & Hiring Committee</strong><br>Azyntrix Technologies</p>
    </div>
    <div class="footer">
      <p style="margin: 0;">© 2026 Azyntrix Technologies Inc. All rights reserved.</p>
    </div>
  </div>
</body>
</html>
"""

    def build_offer_letter_html(
        self,
        candidate_name: str,
        role: str,
        salary_lpa: str,
        joining_date: str = "October 15, 2026",
        reporting_manager: str = "Director of Engineering",
        location: str = "Bengaluru / Remote Hybrid"
    ) -> str:
        """Generate high-impact branded HTML email for Stage 3: Official Offer Letter & Kit."""
        return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; margin: 0; padding: 20px; color: #1e293b; }}
    .container {{ max-width: 640px; margin: 0 auto; background: #ffffff; border-radius: 14px; overflow: hidden; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.3); }}
    .header {{ background: linear-gradient(135deg, #059669, #0d9488, #0284c7); padding: 36px 30px; text-align: center; color: #ffffff; }}
    .content {{ padding: 32px; line-height: 1.6; font-size: 15px; }}
    .table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
    .table th, .table td {{ padding: 12px 14px; border: 1px solid #e2e8f0; font-size: 14px; }}
    .table th {{ background: #f8fafc; font-weight: 600; text-align: left; color: #475569; }}
    .highlight {{ background: #ecfdf5; border-left: 4px solid #10b981; padding: 16px; border-radius: 6px; margin: 20px 0; }}
    .btn {{ display: inline-block; background: #059669; color: #ffffff !important; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 700; margin: 15px 0; font-size: 15px; letter-spacing: 0.3px; }}
    .footer {{ background: #f8fafc; padding: 24px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div style="font-size: 13px; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.9; margin-bottom: 6px;">Azyntrix Technologies Inc.</div>
      <h1 style="margin: 0; font-size: 26px; font-weight: 800;">Official Offer of Employment</h1>
      <p style="margin: 8px 0 0 0; opacity: 0.95; font-size: 15px;">Stage 3: Offer Letter & Executive Welcome Package</p>
    </div>
    <div class="content">
      <p>Dear <strong>{candidate_name}</strong>,</p>
      <p>On behalf of the executive leadership at <strong>Azyntrix Technologies</strong>, we are thrilled to extend this formal offer of employment for the role of <strong>{role}</strong>.</p>
      
      <div class="highlight">
        <h3 style="margin: 0 0 6px 0; color: #047857; font-size: 16px;">🎉 Position & Compensation Summary</h3>
        <p style="margin: 0; color: #065f46; font-size: 14px;">We are excited about the talent, expertise, and leadership you bring to our team.</p>
      </div>

      <table class="table">
        <tr>
          <th>Designation / Role</th>
          <td><strong>{role}</strong></td>
        </tr>
        <tr>
          <th>Annual Cost to Company (CTC)</th>
          <td><strong style="color: #059669; font-size: 16px;">₹ {salary_lpa} LPA</strong> (Gross)</td>
        </tr>
        <tr>
          <th>Start / Joining Date</th>
          <td><strong>{joining_date}</strong></td>
        </tr>
        <tr>
          <th>Reporting Manager</th>
          <td>{reporting_manager}</td>
        </tr>
        <tr>
          <th>Workplace Model</th>
          <td>{location}</td>
        </tr>
        <tr>
          <th>Benefits Package</th>
          <td>Comprehensive Medical Cover (₹10L), Annual Tech Stipend, Performance Equity Units (ESOPs)</td>
        </tr>
      </table>

      <div style="text-align: center; margin: 25px 0;">
        <p style="font-weight: 600; color: #1e293b; margin-bottom: 8px;">To accept this offer, please reply to this email with "I Accept":</p>
        <a href="mailto:{self.sender_email}?subject=Acceptance of Offer - {candidate_name} ({role})&body=I, {candidate_name}, formally accept the offer of employment for the position of {role}." class="btn">Click Here to Accept Offer</a>
      </div>

      <p style="font-size: 13px; color: #64748b;">This offer is contingent upon successful verification of references and background records. Please confirm your acceptance within 5 business days.</p>
      
      <p>Welcome aboard!<br><strong>Executive People Operations & Leadership Team</strong><br>Azyntrix Technologies Inc.</p>
    </div>
    <div class="footer">
      <p style="margin: 0 0 6px 0;">© 2026 Azyntrix Technologies Inc. · All Rights Reserved.</p>
      <p style="margin: 0;">Authorized Google Workspace Dispatch: <code>{self.sender_email}</code></p>
    </div>
  </div>
</body>
</html>
"""

# Global singleton instance
gmail_client = GmailClient()

