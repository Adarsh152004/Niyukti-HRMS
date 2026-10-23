"""
Program 22 — Real WhatsApp Webhook Controller.

POST /api/v1/integrations/whatsapp/webhook — receive messages
GET  /api/v1/integrations/whatsapp/webhook — Meta hub verification
"""
from __future__ import annotations
import json, logging, os, uuid
from typing import Any
from fastapi import APIRouter, HTTPException, Query, Request, Response
from urllib.parse import parse_qs

from backend.integrations.whatsapp_provider import build_whatsapp_provider, WAOutboundMessage
from backend.integrations.identity_resolver import resolve_phone_principal
from backend.agents.orchestration.ceo_whatsapp_orchestrator import handle_ceo_message

logger = logging.getLogger("hrms.whatsapp_webhook")
router = APIRouter(prefix="/api/v1/integrations/whatsapp", tags=["WhatsApp"])

def get_provider() -> Any:
    return build_whatsapp_provider()

@router.get("/webhook", summary="Meta webhook hub verification")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """Meta calls this to verify the webhook URL during setup."""
    expected_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "hrms-webhook-verify")
    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        logger.info("WhatsApp webhook verified by Meta")
        return Response(content=hub_challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Webhook verification failed")

@router.post("/webhook", summary="Receive inbound WhatsApp messages")
async def receive_whatsapp(request: Request):
    """
    Receives inbound WhatsApp messages from OpenWA, Meta or Twilio.
    Supports both application/json and application/x-www-form-urlencoded.
    1. Verifies signature
    2. Resolves sender to CEO identity
    3. Routes to AI orchestrator
    4. Sends response back via WhatsApp
    """
    body_bytes = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    provider = get_provider()

    # 1. Signature verification
    sig_ok = await provider.verify_webhook_signature(body_bytes, signature)
    if not sig_ok:
        logger.warning("WhatsApp webhook signature verification failed")
        raise HTTPException(status_code=403, detail="Invalid webhook signature")

    # 2. Parse payload flexible
    payload: dict[str, Any] = {}
    if body_bytes:
        try:
            payload = json.loads(body_bytes.decode("utf-8"))
        except Exception:
            parsed = parse_qs(body_bytes.decode("utf-8"))
            payload = {k: v[0] for k, v in parsed.items()}

    msg = await provider.parse_inbound_message(payload)
    if not msg:
        return {"status": "no_message"}

    logger.info(f"Inbound WhatsApp from {msg.from_number[:6]}***: {msg.body[:80]}")

    # 3. Identity resolution (server-side only — never trust claimed identity)
    principal = resolve_phone_principal(msg.from_number)
    if not principal:
        logger.warning(f"Unauthorized WhatsApp sender: {msg.from_number[:6]}***")
        # Don't reveal system exists to unauthorized numbers
        return {"status": "ok"}

    # 4. Route to CEO orchestrator
    try:
        response_text = await handle_ceo_message(
            phone=msg.from_number,
            message_body=msg.body,
            principal=principal,
        )
    except Exception as e:
        logger.error(f"Orchestrator error: {e}")
        response_text = "I encountered an error processing your request. Please try again."

    # 5. Send response back via WhatsApp
    result = await provider.send_message(
        WAOutboundMessage(to_number=msg.from_number, body=response_text)
    )
    logger.info(f"WhatsApp response sent: {result.status} id={result.provider_message_id}")

    return {
        "status": "processed",
        "message_id": msg.message_id,
        "from": msg.from_number,
        "ceo_authorized": True,
        "response_text": response_text,
        "response_sent": result.success,
        "provider_status": result.status,
    }
