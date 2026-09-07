
"""
Program 22 — CEO Phone → AuthPrincipal resolver.
Server-side only. Never trusts user-supplied claims.
"""
from __future__ import annotations
import os, re
from backend.api.middleware.auth import AuthPrincipal

CEO_CAPABILITIES = [
    "EXECUTIVE_READ","EXECUTIVE_ANALYTICS","EXECUTIVE_WRITE",
    "RECRUITMENT_COMMAND","RECRUITMENT_READ","RECRUITMENT_WRITE",
    "HIRING_APPROVAL","WORKFORCE_PLANNING","AI_ORCHESTRATION",
    "PAYROLL_READ","PAYROLL_APPROVAL","EMPLOYEE_READ","EMPLOYEE_WRITE",
    "ANALYTICS_READ","KNOWLEDGE_READ","NOTIFICATION_WRITE",
    "HITL_APPROVE","KILL_SWITCH","AGENT_CONTROL",
]

def normalize_phone(raw: str) -> str:
    phone = re.sub(r"[^\d+]", "", raw.strip().replace("whatsapp:",""))
    if not phone.startswith("+"):
        if phone.startswith("91") and len(phone) >= 12: phone = "+"+phone
        elif len(phone) == 10: phone = "+91"+phone
        else: phone = "+"+phone
    return phone

def resolve_phone_principal(raw_phone: str) -> AuthPrincipal | None:
    """
    Resolve verified sender phone to AuthPrincipal.
    Returns None if number not registered (unauthorized).
    """
    phone = normalize_phone(raw_phone)
    ceo_raw = os.getenv("CEO_PHONE_NUMBER","")
    if not ceo_raw:
        return None
    if phone == normalize_phone(ceo_raw):
        return AuthPrincipal(
            user_id="ceo-001",
            tenant_id=os.getenv("TENANT_ID","org-apex-01"),
            roles=["CEO","SUPER_ADMIN","HR_ADMIN"],
            scopes=CEO_CAPABILITIES,
            actor_type="CEO_WHATSAPP",
            email=os.getenv("CEO_EMAIL","ceo@enterprise.demo"),
            risk_tier="LOW",
        )
    return None  # Unauthorized number
