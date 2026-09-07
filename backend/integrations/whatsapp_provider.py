
"""
Program 22 — Real WhatsApp Business Provider.
Supports Meta Cloud API and Twilio. Never fakes success.
"""
from __future__ import annotations
import hashlib, hmac, json, logging, os, time, uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
import httpx

logger = logging.getLogger("hrms.whatsapp")

class IntegrationStatus(StrEnum):
    LIVE = "LIVE"
    CONFIGURED_BUT_NOT_VERIFIED = "CONFIGURED_BUT_NOT_VERIFIED"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    MOCK = "MOCK"
    ERROR = "ERROR"

@dataclass
class WAInboundMessage:
    message_id: str
    from_number: str
    to_number: str
    body: str
    message_type: str = "text"
    timestamp: str = ""
    provider_message_id: str = ""
    raw_payload: dict = field(default_factory=dict)

@dataclass
class WAOutboundMessage:
    to_number: str
    body: str

@dataclass
class WASendResult:
    success: bool
    provider_message_id: str = ""
    error: str = ""
    status: str = "UNKNOWN"

class WhatsAppProvider(ABC):
    @abstractmethod
    async def verify_webhook_signature(self, payload: bytes, signature: str) -> bool: ...
    @abstractmethod
    async def parse_inbound_message(self, payload: dict) -> WAInboundMessage | None: ...
    @abstractmethod
    async def send_message(self, msg: WAOutboundMessage) -> WASendResult: ...
    @abstractmethod
    async def get_status(self) -> dict: ...

class MetaWhatsAppProvider(WhatsAppProvider):
    BASE = "https://graph.facebook.com/v19.0"
    def __init__(self):
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID","")
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN","")
        self.app_secret = os.getenv("WHATSAPP_APP_SECRET","")
        self._cache = {}; self._cache_t = 0

    def _ok(self): return bool(self.phone_number_id and self.access_token)

    async def verify_webhook_signature(self, payload: bytes, sig: str) -> bool:
        if not self.app_secret: return True
        exp = "sha256=" + hmac.new(self.app_secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(exp, sig)

    async def parse_inbound_message(self, payload: dict) -> WAInboundMessage | None:
        try:
            msgs = payload.get("entry",[{}])[0].get("changes",[{}])[0].get("value",{}).get("messages",[])
            if not msgs: return None
            m = msgs[0]
            return WAInboundMessage(
                message_id=str(uuid.uuid4()),
                from_number="+"+m.get("from","").lstrip("+"),
                to_number=payload.get("entry",[{}])[0].get("changes",[{}])[0].get("value",{}).get("metadata",{}).get("display_phone_number",""),
                body=m.get("text",{}).get("body",""),
                message_type=m.get("type","text"),
                timestamp=m.get("timestamp",""),
                provider_message_id=m.get("id",""),
                raw_payload=payload,
            )
        except Exception as e:
            logger.error(f"Meta parse error: {e}"); return None

    async def send_message(self, msg: WAOutboundMessage) -> WASendResult:
        if not self._ok():
            return WASendResult(False, error="Meta credentials not configured", status="NOT_CONFIGURED")
        try:
            async with httpx.AsyncClient(timeout=15) as c:
                resp = await c.post(
                    f"{self.BASE}/{self.phone_number_id}/messages",
                    headers={"Authorization":f"Bearer {self.access_token}"},
                    json={"messaging_product":"whatsapp","to":msg.to_number.lstrip("+"),
                          "type":"text","text":{"body":msg.body}},
                )
                d = resp.json()
                if resp.status_code == 200 and "messages" in d:
                    return WASendResult(True, provider_message_id=d["messages"][0].get("id",""), status="SENT")
                return WASendResult(False, error=str(d), status="FAILED")
        except Exception as e:
            return WASendResult(False, error=str(e), status="ERROR")

    async def get_status(self) -> dict:
        now = time.time()
        if self._cache and now - self._cache_t < 60: return self._cache
        if not self._ok():
            r = {"provider":"meta","status":IntegrationStatus.NOT_CONFIGURED,
                 "message":"Set WHATSAPP_PHONE_NUMBER_ID + WHATSAPP_ACCESS_TOKEN"}
            self._cache, self._cache_t = r, now; return r
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                resp = await c.get(f"{self.BASE}/{self.phone_number_id}",
                    headers={"Authorization":f"Bearer {self.access_token}"})
                if resp.status_code == 200:
                    d = resp.json()
                    r = {"provider":"meta","status":IntegrationStatus.LIVE,
                         "phone":d.get("display_phone_number"),
                         "name":d.get("verified_name")}
                else:
                    r = {"provider":"meta","status":IntegrationStatus.CONFIGURED_BUT_NOT_VERIFIED,
                         "message":f"HTTP {resp.status_code}"}
        except Exception as e:
            r = {"provider":"meta","status":IntegrationStatus.ERROR,"message":str(e)}
        self._cache, self._cache_t = r, now; return r

class TwilioWhatsAppProvider(WhatsAppProvider):
    def __init__(self):
        self.sid = os.getenv("TWILIO_ACCOUNT_SID","")
        self.token = os.getenv("TWILIO_AUTH_TOKEN","")
        self.from_num = os.getenv("TWILIO_WHATSAPP_FROM","")
        self._cache = {}; self._cache_t = 0

    def _ok(self): return bool(self.sid and self.token and self.from_num)

    async def verify_webhook_signature(self, payload: bytes, sig: str) -> bool: return True

    async def parse_inbound_message(self, payload: dict) -> WAInboundMessage | None:
        from_num = payload.get("From","").replace("whatsapp:","")
        body = payload.get("Body","")
        if not from_num or not body: return None
        return WAInboundMessage(
            message_id=str(uuid.uuid4()),
            from_number=from_num,
            to_number=payload.get("To","").replace("whatsapp:",""),
            body=body, timestamp=str(int(time.time())),
            provider_message_id=payload.get("MessageSid",""),
            raw_payload=payload,
        )

    async def send_message(self, msg: WAOutboundMessage) -> WASendResult:
        if not self._ok():
            return WASendResult(False, error="Twilio not configured", status="NOT_CONFIGURED")
        try:
            to = f"whatsapp:{msg.to_number}" if not msg.to_number.startswith("whatsapp:") else msg.to_number
            async with httpx.AsyncClient(timeout=15) as c:
                resp = await c.post(
                    f"https://api.twilio.com/2010-04-01/Accounts/{self.sid}/Messages.json",
                    data={"From":self.from_num,"To":to,"Body":msg.body},
                    auth=(self.sid, self.token),
                )
                d = resp.json()
                if resp.status_code in (200,201):
                    return WASendResult(True, provider_message_id=d.get("sid",""), status="SENT")
                return WASendResult(False, error=d.get("message",""), status="FAILED")
        except Exception as e:
            return WASendResult(False, error=str(e), status="ERROR")

    async def get_status(self) -> dict:
        now = time.time()
        if self._cache and now - self._cache_t < 60: return self._cache
        if not self._ok():
            r = {"provider":"twilio","status":IntegrationStatus.NOT_CONFIGURED,
                 "message":"Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM"}
            self._cache, self._cache_t = r, now; return r
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                resp = await c.get(
                    f"https://api.twilio.com/2010-04-01/Accounts/{self.sid}.json",
                    auth=(self.sid, self.token),
                )
                if resp.status_code == 200:
                    d = resp.json()
                    r = {"provider":"twilio","status":IntegrationStatus.LIVE,
                         "friendly_name":d.get("friendly_name")}
                else:
                    r = {"provider":"twilio","status":IntegrationStatus.CONFIGURED_BUT_NOT_VERIFIED,
                         "message":f"HTTP {resp.status_code}"}
        except Exception as e:
            r = {"provider":"twilio","status":IntegrationStatus.ERROR,"message":str(e)}
        self._cache, self._cache_t = r, now; return r

class MockWhatsAppProvider(WhatsAppProvider):
    def __init__(self):
        self.sent: list[dict] = []
        self.received: list[WAInboundMessage] = []

    async def verify_webhook_signature(self, payload: bytes, sig: str) -> bool: return True

    async def parse_inbound_message(self, payload: dict) -> WAInboundMessage | None:
        body = payload.get("Body","")
        if not body: return None
        m = WAInboundMessage(
            message_id=str(uuid.uuid4()),
            from_number=payload.get("From","+15550000000"),
            to_number=payload.get("To","+15551111111"),
            body=body, timestamp=str(int(time.time())), raw_payload=payload,
        )
        self.received.append(m); return m

    async def send_message(self, msg: WAOutboundMessage) -> WASendResult:
        mid = f"mock-wa-{uuid.uuid4().hex[:8]}"
        self.sent.append({"id":mid,"to":msg.to_number,"body":msg.body,"ts":time.time()})
        logger.info(f"[MOCK WA] → {msg.to_number}: {msg.body[:100]}")
        return WASendResult(True, provider_message_id=mid, status="MOCK_SENT")

    async def get_status(self) -> dict:
        return {"provider":"mock","status":IntegrationStatus.MOCK,
                "message":"MOCK mode. Set WHATSAPP_PROVIDER=meta or twilio for real integration.",
                "sent_count":len(self.sent)}

def build_whatsapp_provider() -> WhatsAppProvider:
    p = os.getenv("WHATSAPP_PROVIDER","").lower()
    if p == "meta": return MetaWhatsAppProvider()
    elif p == "twilio": return TwilioWhatsAppProvider()
    return MockWhatsAppProvider()

def normalize_phone(raw: str) -> str:
    import re
    phone = re.sub(r"[^\d+]", "", raw.strip().replace("whatsapp:",""))
    if not phone.startswith("+"):
        if phone.startswith("91") and len(phone) >= 12: phone = "+"+phone
        elif len(phone) == 10: phone = "+91"+phone
        else: phone = "+"+phone
    return phone
