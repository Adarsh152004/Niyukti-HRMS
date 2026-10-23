
"""
Program 22 — Live Integration Smoke Test.
Tests actual providers. Never fakes results.

Usage:
  .venv/Scripts/python.exe scripts/smoke_test_live_integrations.py
"""
import asyncio, httpx, os, sys, time
from dotenv import load_dotenv
load_dotenv()

W  = "\033[0m"
G  = "\033[92m"
Y  = "\033[93m"
R  = "\033[91m"
B  = "\033[94m"
BO = "\033[1m"

def row(name, status, detail=""):
    color = G if status == "LIVE" else (Y if "CONFIGURED" in status or "MOCK" in status else R)
    pad = " " * max(1, 30 - len(name))
    det = f"  [{detail}]" if detail else ""
    print(f"  {name}{pad}{color}{status}{W}{det}")

async def main():
    print(f"\n{BO}{'='*60}{W}")
    print(f"{BO}  PROGRAM 22 — LIVE INTEGRATION STATUS MATRIX{W}")
    print(f"{BO}{'='*60}{W}")
    print()

    # 1. Backend
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get("http://127.0.0.1:8000/health/live")
            row("BACKEND API", "LIVE" if r.status_code==200 else "ERROR", f"HTTP {r.status_code}")
    except Exception as e:
        row("BACKEND API", "DOWN", str(e)[:50])

    # 2. Integration status matrix from backend
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.get("http://127.0.0.1:8000/api/v1/integrations/status")
            if r.status_code == 200:
                data = r.json()
                for name, info in data.get("integrations",{}).items():
                    status = info.get("status","UNKNOWN")
                    msg = info.get("message","")
                    row(name.upper(), status, msg[:50])
            else:
                row("INTEGRATION STATUS API", "ERROR", f"HTTP {r.status_code}")
    except Exception as e:
        row("INTEGRATION STATUS API", "DOWN", str(e)[:50])

    # 3. Direct AI test
    gemini_key = os.getenv("GEMINI_API_KEY","")
    if gemini_key:
        try:
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={gemini_key}",
                    json={"contents":[{"parts":[{"text":"Respond with just: LIVE"}]}]},
                )
                if r.status_code == 200:
                    row("GEMINI DIRECT", "LIVE", "gemini-3.6-flash")
                else:
                    row("GEMINI DIRECT", "ERROR", f"HTTP {r.status_code}")
        except Exception as e:
            row("GEMINI DIRECT", "DOWN", str(e)[:50])

    # 4. Groq direct
    groq_key = os.getenv("GROQ_API_KEY","")
    if groq_key:
        try:
            async with httpx.AsyncClient(timeout=15) as c:
                r = await c.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization":f"Bearer {groq_key}"},
                    json={"model":"openai/gpt-oss-20b","messages":[{"role":"user","content":"LIVE"}]},
                )
                row("GROQ DIRECT", "LIVE" if r.status_code==200 else "ERROR",
                    f"HTTP {r.status_code}")
        except Exception as e:
            row("GROQ DIRECT", "DOWN", str(e)[:50])

    # 5. WhatsApp
    wa_provider = os.getenv("WHATSAPP_PROVIDER","")
    wa_phone_id = bool(os.getenv("WHATSAPP_PHONE_NUMBER_ID",""))
    wa_twilio = bool(os.getenv("TWILIO_ACCOUNT_SID",""))
    if wa_provider == "meta" and wa_phone_id:
        row("WHATSAPP (META)", "CONFIGURED_BUT_NOT_VERIFIED", "Verify at Meta Business Dashboard")
    elif wa_provider == "twilio" and wa_twilio:
        row("WHATSAPP (TWILIO)", "CONFIGURED_BUT_NOT_VERIFIED", "Run Twilio verify")
    else:
        row("WHATSAPP", "NOT_CONFIGURED",
            "Set WHATSAPP_PROVIDER=meta or twilio + credentials")

    # 6. CEO Identity
    ceo_phone = bool(os.getenv("CEO_PHONE_NUMBER",""))
    row("CEO_PHONE_NUMBER", "LIVE" if ceo_phone else "NOT_CONFIGURED",
        "CEO identity configured" if ceo_phone else "Set CEO_PHONE_NUMBER=+91XXXXXXXXXX")

    # 7. Email
    smtp = os.getenv("SMTP_HOST","")
    gmail = os.getenv("GOOGLE_CLIENT_ID","")
    if smtp: row("EMAIL (SMTP)", "CONFIGURED_BUT_NOT_VERIFIED", smtp)
    elif gmail: row("EMAIL (GMAIL)", "CONFIGURED_BUT_NOT_VERIFIED", "OAuth configured")
    else: row("EMAIL", "NOT_CONFIGURED", "Set SMTP_HOST or GOOGLE_CLIENT_ID")

    # 8. LinkedIn
    li = bool(os.getenv("LINKEDIN_ACCESS_TOKEN",""))
    row("LINKEDIN", "CONFIGURED_BUT_NOT_VERIFIED" if li else "NOT_CONFIGURED",
        "Token present" if li else "Set LINKEDIN_ACCESS_TOKEN + LINKEDIN_ORGANIZATION_ID")

    # 9. Calendar
    gcal = bool(os.getenv("GOOGLE_CLIENT_ID","")) and bool(os.getenv("GOOGLE_REFRESH_TOKEN",""))
    row("GOOGLE CALENDAR", "CONFIGURED_BUT_NOT_VERIFIED" if gcal else "NOT_CONFIGURED",
        "OAuth configured" if gcal else "Set GOOGLE_CLIENT_ID + GOOGLE_REFRESH_TOKEN")

    # 10. Redis
    try:
        import redis as rl
        r = rl.from_url(os.getenv("REDIS_URL","redis://localhost:6379"), socket_timeout=2)
        r.ping()
        row("REDIS", "LIVE")
    except Exception as e:
        row("REDIS", "NOT_CONFIGURED", "Start Redis: docker run -p 6379:6379 redis:7-alpine")

    print()
    print(f"{BO}SETUP GUIDE:{W}")
    print("  1. WhatsApp: Set WHATSAPP_PROVIDER=meta + Meta Cloud API creds in .env")
    print("  2. CEO Phone: Set CEO_PHONE_NUMBER=+91XXXXXXXXXX in .env")
    print("  3. Email:     Set SMTP_HOST/SMTP_PORT/SMTP_USER/SMTP_PASS in .env")
    print("  4. LinkedIn:  Set LINKEDIN_ACCESS_TOKEN + LINKEDIN_ORGANIZATION_ID in .env")
    print("  5. Calendar:  Set GOOGLE_CLIENT_ID + GOOGLE_REFRESH_TOKEN in .env")
    print("  6. Redis:     docker run -d -p 6379:6379 redis:7-alpine")
    print()
    print(f"  See: docs/PROGRAM_22_LIVE_SETUP.md for full setup instructions")
    print()

asyncio.run(main())
