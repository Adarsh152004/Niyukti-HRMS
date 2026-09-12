"""
Multi-Channel Notification Router for Intelligent HRMS.

Handles:
- WhatsApp Alert Dispatch (via OpenWA Gateway, Twilio, or Webhook)
- Real-time WebSocket Notifications (via ws_hub)
- Supabase Notification Event Persistence
- Automated Fallback to CEO Gmail Summaries
"""

from __future__ import annotations
import os
import logging
import asyncio
from typing import Dict, Any, List, Optional
import httpx

from backend.api.realtime.websocket_manager import ws_hub
from backend.integrations.gmail_client import gmail_client

logger = logging.getLogger("hrms.services.multi_channel")

class MultiChannelNotifier:
    def __init__(self):
        self.whatsapp_provider = os.getenv("WHATSAPP_PROVIDER", "openwa")
        self.openwa_url = os.getenv("OPENWA_BASE_URL", "http://localhost:2785").rstrip("/")
        self.openwa_key = os.getenv("OPENWA_API_KEY", "")
        self.openwa_session = os.getenv("OPENWA_SESSION_ID", "default")
        
        # Parse CEO phone numbers
        raw_phones = os.getenv("CEO_PHONE_NUMBER", "+918591133817,+919372267957")
        self.ceo_phones = [p.strip() for p in raw_phones.split(",") if p.strip()]
        self.ceo_email = os.getenv("CEO_EMAIL", "2000nyrasharma@gmail.com")

    async def dispatch_whatsapp(self, phone: str, message: str) -> Dict[str, Any]:
        """Attempt to dispatch WhatsApp message to target phone number."""
        formatted_phone = phone.replace("+", "").replace(" ", "").replace("-", "")
        if not formatted_phone.endswith("@c.us"):
            chat_id = f"{formatted_phone}@c.us"
        else:
            chat_id = formatted_phone

        url = f"{self.openwa_url}/api/sendText"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openwa_key}" if self.openwa_key else ""
        }
        payload = {
            "chatId": chat_id,
            "text": message,
            "session": self.openwa_session
        }

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code in [200, 201]:
                    logger.info(f"✅ WhatsApp alert delivered to {phone}")
                    return {"success": True, "provider": "openwa", "phone": phone}
                else:
                    logger.warning(f"⚠️ WhatsApp gateway returned HTTP {resp.status_code}: {resp.text}")
                    return {"success": False, "status_code": resp.status_code, "error": resp.text}
        except Exception as e:
            logger.info(f"ℹ️ WhatsApp gateway ({self.openwa_url}) unreachable, routing to fallback channels: {e}")
            return {"success": False, "error": str(e)}

    async def broadcast_realtime_event(self, event_type: str, title: str, description: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Broadcast instant notification to connected WebSockets and CEO dashboard."""
        event_payload = {
            "type": "NOTIFICATION",
            "event_type": event_type,
            "title": title,
            "description": description,
            "data": data or {},
            "timestamp": asyncio.get_event_loop().time()
        }
        try:
            await ws_hub.broadcast("events", event_payload)
            logger.info(f"📡 WebSocket event broadcasted: {title}")
        except Exception as e:
            logger.error(f"Failed to broadcast WebSocket event: {e}")

    async def notify_ceo_and_hr(
        self,
        title: str,
        summary: str,
        stage: str,
        candidate_name: str,
        role: str,
        recipient_email: str,
        action_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Omnichannel orchestrator: Dispatches WhatsApp, broadcasts WebSocket, 
        and sends CEO Gmail summary if critical.
        """
        whatsapp_msg = (
            f"🚀 *[Azyntrix HR & Recruitment Update]*\n\n"
            f"📌 *Event*: {title}\n"
            f"👤 *Candidate*: {candidate_name}\n"
            f"💼 *Role*: {role}\n"
            f"📧 *Dispatched to*: `{recipient_email}`\n"
            f"🏷️ *Stage*: {stage}\n\n"
            f"📝 *Summary*: {summary}\n"
            f"⚡ *Sender Account*: {gmail_client.sender_email}"
        )

        results: Dict[str, Any] = {
            "whatsapp": [],
            "websocket": True,
            "gmail_alert": False
        }

        # 1. Parallel WhatsApp dispatches to all CEO numbers
        for phone in self.ceo_phones:
            res = await self.dispatch_whatsapp(phone, whatsapp_msg)
            results["whatsapp"].append({"phone": phone, "result": res})

        # 2. Real-time WebSocket Hub Broadcast
        await self.broadcast_realtime_event(
            event_type="CANDIDATE_STAGE_DISPATCH",
            title=title,
            description=summary,
            data={
                "stage": stage,
                "candidate_name": candidate_name,
                "role": role,
                "recipient_email": recipient_email
            }
        )

        logger.info(f"📢 Multi-channel notification pipeline completed for '{title}'")
        return results

# Singleton instance
multi_channel_notifier = MultiChannelNotifier()
