"""
Tests for Multi-Agent Business Operations Teams Execution.
"""

from __future__ import annotations

import pytest

from backend.agents.operations.teams.executive_team import AutonomousExecutiveTeam
from backend.agents.operations.teams.recruitment_team import AutonomousRecruitmentTeam
from backend.agents.operations.teams.workforce_team import AutonomousWorkforceOperationsTeam


@pytest.mark.asyncio
async def test_recruitment_team_coordination():
    org_id = "org-team-rec"
    team = AutonomousRecruitmentTeam(org_id)

    res = await team.execute_team_operation(
        operation_name="screen_and_rank_candidates",
        parameters={"job_id": "job-777", "candidates": [{"id": "c1"}, {"id": "c2"}, {"id": "c3"}]},
    )

    assert res["status"] == "COMPLETED"
    assert res["job_id"] == "job-777"
    assert res["screening_message_id"] is not None
    assert res["ranking_message_id"] is not None


@pytest.mark.asyncio
async def test_workforce_operations_team_coordination():
    org_id = "org-team-workforce"
    team = AutonomousWorkforceOperationsTeam(org_id)

    res = await team.execute_team_operation(
        operation_name="monthly_reconciliation_and_payroll_prep",
        parameters={"month": "2026-08"},
    )

    assert res["status"] == "COMPLETED"
    assert res["month"] == "2026-08"
    assert res["attendance_audit_msg_id"] is not None
    assert res["payroll_prep_msg_id"] is not None


@pytest.mark.asyncio
async def test_executive_strategic_team_coordination():
    org_id = "org-team-exec"
    team = AutonomousExecutiveTeam(org_id)

    res = await team.execute_team_operation(
        operation_name="quarterly_strategic_risk_assessment",
        parameters={"quarter": "Q3-2026"},
    )

    assert res["status"] == "COMPLETED"
    assert res["quarter"] == "Q3-2026"
    assert res["attrition_scan_msg_id"] is not None
    assert res["compliance_audit_msg_id"] is not None
