"""
AI-Powered Intelligent HRMS — Live Integrations Test Suite (WhatsApp, LinkedIn, Email, MCP Tools).

Verifies:
1. Inbound WhatsApp webhook parsing and approval routing
2. Outbound WhatsApp message queueing
3. LinkedIn / Job Board requisition publishing
4. Agent Email Inbox polling and candidate resume ingestion
5. Governed MCP Server new tools execution & HITL gating
"""

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.mcp.schemas import MCPCallToolRequest
from backend.mcp.server import GovernedMCPServer

client = TestClient(app)


def test_whatsapp_inbound_webhook_and_approval_routing():
    """Verify incoming WhatsApp approval command routes directly to HITL layer."""
    # 1. Standard inbound WhatsApp chat message
    res = client.post(
        "/api/v1/integrations/whatsapp/webhook",
        json={"From": "+14155552671", "To": "+14155238886", "Body": "Hello AI HRMS, give me headcount status."},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "RECEIVED"

    # 2. Inbound WhatsApp one-word approval command
    res_appr = client.post(
        "/api/v1/integrations/whatsapp/webhook",
        json={"From": "+14155552671", "To": "+14155238886", "Body": "APPROVE hitl-mcp-9901"},
    )
    assert res_appr.status_code == 200
    assert res_appr.json()["action"] == "APPROVE"
    assert res_appr.json()["approval_id"] == "hitl-mcp-9901"


def test_linkedin_job_board_publishing():
    """Verify job requisition publication to LinkedIn / Job Boards."""
    # Authenticate SuperAdmin
    client.post(
        "/api/v1/auth/register",
        json={
            "organization_id": "org-apex-01",
            "username": "admin_li_test",
            "email": "admin_li@enterprise.demo",
            "password": "Password123!@#Secure",
        },
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": "org-apex-01",
            "email": "admin_li@enterprise.demo",
            "password": "Password123!@#Secure",
        },
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": "org-apex-01"}

    # Publish Job
    res = client.post(
        "/api/v1/integrations/jobs/publish",
        headers=headers,
        json={
            "requisition_id": "req-eng-101",
            "title": "Principal Distributed Systems Architect",
            "department": "Engineering",
            "location": "San Francisco, CA / Remote",
            "employment_type": "FULL_TIME",
            "description": "Lead architecture of scalable agentic AI systems.",
            "requirements": ["10+ years backend engineering", "Python", "FastAPI", "PostgreSQL"],
            "skills": ["Distributed Systems", "Python", "FastAPI", "Docker", "Kubernetes"],
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "PUBLISHED"
    assert "linkedin.com/jobs" in data["url"]


def test_email_inbox_polling_for_resumes():
    """Verify agent can check email inbox for unread candidate resumes."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": "org-apex-01",
            "email": "admin_li@enterprise.demo",
            "password": "Password123!@#Secure",
        },
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": "org-apex-01"}

    res = client.get("/api/v1/integrations/email/inbox", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["unread_count"] >= 1
    assert "Application for Senior Backend Engineer" in data["messages"][0]["subject"]


@pytest.mark.asyncio
async def test_mcp_recruitment_and_external_tools():
    """Verify governed MCP server executes recruitment, job board, and communication tools."""
    mcp = GovernedMCPServer.get_instance()

    # 1. Job Board Post Tool
    res_job = await mcp.execute_tool(MCPCallToolRequest(
        tool_name="job_board.post_job",
        arguments={"requisition_id": "req-01", "title": "Staff Engineer", "platform": "LINKEDIN"},
        tenant_id="org-apex-01",
        actor_id="usr-recruiter-01",
    ))
    assert res_job.success is True
    assert res_job.data["platform"] == "LINKEDIN"

    # 2. Resume Parsing Tool
    res_parse = await mcp.execute_tool(MCPCallToolRequest(
        tool_name="recruitment.parse_resume",
        arguments={"resume_url": "https://storage.enterprise.demo/resumes/aarav.pdf"},
        tenant_id="org-apex-01",
        actor_id="usr-recruiter-01",
    ))
    assert res_parse.success is True
    assert "Python" in res_parse.data["skills"]

    # 3. Candidate Ranking Tool
    res_rank = await mcp.execute_tool(MCPCallToolRequest(
        tool_name="recruitment.rank_candidates",
        arguments={"requisition_id": "req-01"},
        tenant_id="org-apex-01",
        actor_id="usr-recruiter-01",
    ))
    assert res_rank.success is True
    assert len(res_rank.data) >= 2
    assert res_rank.data[0]["match_score"] >= 90.0

    # 4. WhatsApp Alert Tool
    res_wa = await mcp.execute_tool(MCPCallToolRequest(
        tool_name="whatsapp.send_alert",
        arguments={"to_number": "+14155552671", "message": "Urgent: Approval required for salary adjustment."},
        tenant_id="org-apex-01",
        actor_id="usr-system",
    ))
    assert res_wa.success is True
    assert res_wa.data["status"] == "DELIVERED"

    # 5. Critical Risk Tool (Employee Terminate -> must halt for HITL)
    res_term = await mcp.execute_tool(MCPCallToolRequest(
        tool_name="employee.terminate",
        arguments={"employee_id": "emp-009", "reason": "Gross misconduct"},
        tenant_id="org-apex-01",
        actor_id="usr-hr",
    ))
    assert res_term.requires_approval is True
    assert res_term.approval_request_id is not None
