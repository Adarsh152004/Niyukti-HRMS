"""
Tests for all 9 Internal MCP Servers.
"""

from __future__ import annotations

import pytest

from backend.mcp.client.client import MCPClient


@pytest.mark.asyncio
async def test_all_nine_mcp_servers_execute_successfully():
    client = MCPClient.get_instance()
    tenant = "org-mcp-9-servers"
    actor = "actor-tester"
    agent = "agent-tester"

    test_invocations = [
        ("hrms.get_employee", {"employee_id": "emp-101"}),
        ("hrms.list_employees", {"department_id": "dept-eng"}),
        ("knowledge.search_policies", {"query": "annual leave"}),
        ("analytics.get_headcount_stats", {}),
        ("workflow.get_instance_status", {"workflow_id": "wf-888"}),
        ("document.extract_metadata", {"document_id": "doc-555"}),
        ("recruitment.get_job_requisition", {"job_id": "job-777"}),
        ("payroll.explain_payslip_breakdown", {"employee_id": "emp-101", "cycle_month": "2026-08"}),
        ("notification.dispatch_template", {"template_id": "tpl-leave-approved", "recipient_id": "emp-101"}),
        ("reporting.build_executive_summary", {"period_quarter": "2026-Q3"}),
    ]

    for tool_id, args in test_invocations:
        resp = await client.call_tool(
            tool_id=tool_id,
            arguments=args,
            tenant_id=tenant,
            actor_id=actor,
            agent_id=agent,
        )
        assert resp.success is True, f"Failed tool: {tool_id}, error: {resp.error}"
        assert resp.result is not None
        assert resp.latency_ms >= 0
