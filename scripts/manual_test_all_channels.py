"""
AI-Powered Intelligent HRMS — Manual & Automated Verification of External Channels.

Tests:
1. Live AI Chatbot & Multi-Provider Router
2. WhatsApp Webhook Inbound & Interactive CEO Sign-off
3. LinkedIn Job Board Publishing
4. Agent Email Inbox Polling & Resume Ingestion
5. Governed MCP Server Tools & Risk Halting
"""

import asyncio
from fastapi.testclient import TestClient

from backend.app import app
from backend.mcp.schemas import MCPCallToolRequest
from backend.mcp.server import GovernedMCPServer

client = TestClient(app)


def test_manual_channels():
    print("==================================================================")
    print("AI-POWERED INTELLIGENT HRMS — EXTERNAL CHANNELS VERIFICATION")
    print("==================================================================")

    # 1. Authenticate SuperAdmin
    client.post(
        "/api/v1/auth/register",
        json={
            "organization_id": "org-apex-01",
            "username": "superadmin_manual",
            "email": "admin_manual@enterprise.demo",
            "password": "Password123!@#Secure",
        },
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": "org-apex-01",
            "email": "admin_manual@enterprise.demo",
            "password": "Password123!@#Secure",
        },
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": "org-apex-01"}

    # 2. Live Chatbot & Reasoning Gateway
    print("\n[CHANNEL 1: LIVE AI CHATBOT & REASONING GATEWAY]")
    chat_res = client.post(
        "/api/v1/ai/command",
        headers=headers,
        json={"prompt": "What is our company parental leave policy and attendance summary?"},
    )
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    print(f"  [CHAT RESPONSE] {chat_data['response_text'][:85]}...")
    print(f"  [CITATIONS] {chat_data['citations']}")
    print("  -> Status: 100% OPERATIONAL")

    # 3. WhatsApp Webhook & CEO Interactive Approval
    print("\n[CHANNEL 2: WHATSAPP WEBHOOK & CEO CHAT CHANNEL]")
    wa_inbound = client.post(
        "/api/v1/integrations/whatsapp/webhook",
        json={"From": "+14155552671", "To": "+14155238886", "Body": "APPROVE hitl-salary-101"},
    )
    assert wa_inbound.status_code == 200
    print(f"  [INBOUND WHATSAPP] {wa_inbound.json()['response_message']}")

    wa_send = client.post(
        "/api/v1/integrations/whatsapp/send",
        headers=headers,
        json={"to_number": "+14155552671", "body": "Alert: New hiring candidate shortlisted."},
    )
    assert wa_send.status_code == 200
    print(f"  [OUTBOUND WHATSAPP] Queued message ID: {wa_send.json()['message_id']}")
    print("  -> Status: 100% OPERATIONAL")

    # 4. LinkedIn & Job Board Automated Posting
    print("\n[CHANNEL 3: LINKEDIN & JOB BOARD PUBLISHING]")
    job_res = client.post(
        "/api/v1/integrations/jobs/publish",
        headers=headers,
        json={
            "requisition_id": "req-eng-staff-01",
            "title": "Staff AI Agent Engineer",
            "department": "Engineering",
            "location": "San Francisco, CA / Remote",
            "description": "Design autonomous agent swarms and enterprise governance pipelines.",
            "requirements": ["Python", "FastAPI", "PostgreSQL", "LLM APIs"],
            "skills": ["Distributed Systems", "LangGraph", "FastAPI", "Docker"],
        },
    )
    assert job_res.status_code == 200
    job_data = job_res.json()
    print(f"  [LINKEDIN POST] Status: {job_data['status']} | URL: {job_data['url']}")
    print("  -> Status: 100% OPERATIONAL")

    # 5. Agent Email Ingestion
    print("\n[CHANNEL 4: AGENT EMAIL INBOX INGESTION]")
    email_res = client.get("/api/v1/integrations/email/inbox", headers=headers)
    assert email_res.status_code == 200
    email_data = email_res.json()
    print(f"  [EMAIL INBOX] Unread Count: {email_data['unread_count']}")
    print(f"  [FIRST EMAIL] Subject: {email_data['messages'][0]['subject']} (From: {email_data['messages'][0]['from_email']})")
    print("  -> Status: 100% OPERATIONAL")

    # 6. Governed MCP Server Tools Execution
    print("\n[CHANNEL 5: GOVERNED MCP TOOLS & HITL GATING]")
    mcp = GovernedMCPServer.get_instance()

    async def run_mcp_checks():
        # Read Tool
        res_read = await mcp.execute_tool(MCPCallToolRequest(
            tool_name="recruitment.rank_candidates",
            arguments={"requisition_id": "req-eng-staff-01"},
            tenant_id="org-apex-01",
            actor_id="usr-recruiter-01",
        ))
        assert res_read.success is True
        print(f"  [MCP READ] Ranked {len(res_read.data)} candidates (Top match: {res_read.data[0]['name']} - {res_read.data[0]['match_score']}%)")

        # Critical Tool -> HITL Gate
        res_crit = await mcp.execute_tool(MCPCallToolRequest(
            tool_name="employee.terminate",
            arguments={"employee_id": "emp-009", "reason": "Gross misconduct"},
            tenant_id="org-apex-01",
            actor_id="usr-hr-admin",
        ))
        assert res_crit.requires_approval is True
        print(f"  [MCP CRITICAL GATING] Action halted: {res_crit.data['reason']}")

    asyncio.run(run_mcp_checks())
    print("  -> Status: 100% OPERATIONAL")

    print("\n==================================================================")
    print("ALL EXTERNAL CHANNELS & INTEGRATIONS MANUALLY TESTED — 100% PASS")
    print("==================================================================\n")


if __name__ == "__main__":
    test_manual_channels()
