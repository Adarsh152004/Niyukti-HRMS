"""
Unit and Integration Tests for Niyukti HRMS LangGraph Agents, Tools, and LLM Gateway.
"""

import pytest
import asyncio
from backend.agents.tools.db_tools import (
    get_all_employees,
    get_headcount_by_department,
    get_employee_profile,
    get_attendance_summary,
    get_leave_balances,
    get_payroll_summary,
)
from backend.agents.tools.guarded_sql_tool import execute_read_only_sql
from backend.agents.rag.policy_rag import search_company_policies
from backend.agents.llm_gateway import default_gateway


@pytest.mark.asyncio
async def test_get_all_employees():
    """Verify that get_all_employees returns records from sqlite."""
    employees = await get_all_employees.ainvoke({"status": "ACTIVE"})
    assert isinstance(employees, list)
    assert len(employees) >= 11
    # Check required fields
    emp0 = employees[0]
    assert "employee_code" in emp0
    assert "name" in emp0
    assert "department" in emp0


@pytest.mark.asyncio
async def test_get_headcount_by_department():
    """Verify departmental headcount aggregation."""
    headcounts = await get_headcount_by_department.ainvoke({})
    assert isinstance(headcounts, list)
    assert len(headcounts) > 0
    dept_names = [h["department"] for h in headcounts]
    assert any("Engineering" in d or "AI" in d for d in dept_names)


@pytest.mark.asyncio
async def test_get_employee_profile():
    """Verify lookup by employee code."""
    profile = await get_employee_profile.ainvoke({"identifier": "EMP-001"})
    assert profile.get("employee_code") == "EMP-001"
    assert "Vikram" in profile.get("name", "")


@pytest.mark.asyncio
async def test_attendance_and_payroll():
    """Verify attendance and payroll queries."""
    att = await get_attendance_summary.ainvoke({})
    assert "total_employees" in att
    assert att["total_employees"] > 0

    pay = await get_payroll_summary.ainvoke({})
    assert "active_payroll_records" in pay
    assert pay["total_annual_payroll_inr"] > 0


@pytest.mark.asyncio
async def test_guarded_sql_security():
    """Verify guarded SQL tool blocks mutations and allows SELECT."""
    # Disallowed mutation
    bad_res = await execute_read_only_sql.ainvoke({"sql_query": "DROP TABLE employees"})
    assert "error" in bad_res
    assert "Security Violation" in bad_res["error"]

    bad_insert = await execute_read_only_sql.ainvoke({"sql_query": "INSERT INTO employees VALUES (1)"})
    assert "error" in bad_insert

    # Allowed read-only SELECT
    good_res = await execute_read_only_sql.ainvoke({
        "sql_query": "SELECT employee_code, first_name FROM employees LIMIT 5"
    })
    assert good_res.get("success") is True
    assert len(good_res.get("data", [])) > 0


@pytest.mark.asyncio
async def test_policy_rag():
    """Verify policy search retrieves PTO and attendance rules."""
    pto_policies = await search_company_policies.ainvoke({"query": "carry forward unused PTO vacation days"})
    assert isinstance(pto_policies, list)
    assert len(pto_policies) > 0
    assert any("Leave" in p.get("category", "") or "PTO" in p.get("title", "") for p in pto_policies)


@pytest.mark.asyncio
async def test_langgraph_event_streaming():
    """Verify that langgraph_engine emits streaming events."""
    from backend.agents.orchestration.graph import langgraph_engine

    events = []
    async for event in langgraph_engine.astream_events(
        query="What is the total headcount and department breakdown?",
        caller_role="SUPERADMIN",
        client_type="workforce",
    ):
        events.append(event)

    event_types = [e["event"] for e in events]
    assert "thinking" in event_types
    assert "tool_call" in event_types
    assert "tool_result" in event_types
    assert "token" in event_types
    assert "done" in event_types


async def main():
    print("Testing get_all_employees...")
    await test_get_all_employees()
    print("  [PASS] get_all_employees")

    print("Testing get_headcount_by_department...")
    await test_get_headcount_by_department()
    print("  [PASS] get_headcount_by_department")

    print("Testing get_employee_profile...")
    await test_get_employee_profile()
    print("  [PASS] get_employee_profile")

    print("Testing attendance_and_payroll...")
    await test_attendance_and_payroll()
    print("  [PASS] attendance_and_payroll")

    print("Testing guarded_sql_security...")
    await test_guarded_sql_security()
    print("  [PASS] guarded_sql_security")

    print("Testing policy_rag...")
    await test_policy_rag()
    print("  [PASS] policy_rag")

    print("Testing langgraph_event_streaming...")
    await test_langgraph_event_streaming()
    print("  [PASS] langgraph_event_streaming")

    print("\nALL AGENT & DATABASE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(main())
