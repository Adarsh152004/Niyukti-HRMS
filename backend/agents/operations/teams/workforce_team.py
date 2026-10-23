"""
Autonomous Workforce Operations Team — Coordinates day-to-day HR operations (attendance, leaves, payroll, documents, employee support).
"""

from __future__ import annotations

import logging
from typing import Any

from backend.agents.operations.teams.base_team import MultiAgentTeam
from backend.agents.specialized.domain.enums import SpecializedAgentRole

logger = logging.getLogger(__name__)


class AutonomousWorkforceOperationsTeam(MultiAgentTeam):
    """
    Workforce Operations Team:
    - Supervisor: HR_MANAGER_AGENT
    - Workers: ATTENDANCE_AGENT, LEAVE_MANAGEMENT_AGENT, PAYROLL_ASSISTANT_AGENT, DOCUMENT_INTELLIGENCE_AGENT, EMPLOYEE_ASSISTANT_AGENT
    """

    def __init__(self, organization_id: str) -> None:
        super().__init__(
            organization_id=organization_id,
            supervisor_role=SpecializedAgentRole.HR_MANAGER_AGENT,
            worker_roles=[
                SpecializedAgentRole.ATTENDANCE_AGENT,
                SpecializedAgentRole.LEAVE_MANAGEMENT_AGENT,
                SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT,
                SpecializedAgentRole.DOCUMENT_INTELLIGENCE_AGENT,
                SpecializedAgentRole.EMPLOYEE_ASSISTANT_AGENT,
            ],
        )

    async def execute_team_operation(self, operation_name: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Coordinate payroll preparation and attendance/leave reconciliation."""
        if operation_name == "monthly_reconciliation_and_payroll_prep":
            month = parameters.get("month", "2026-08")

            # 1. Delegate attendance audit
            att_msg = await self.delegate_task_to_worker(
                worker_role=SpecializedAgentRole.ATTENDANCE_AGENT,
                task_name="audit_attendance_exceptions",
                payload={"month": month},
            )

            # 2. Delegate leave reconciliation
            leave_msg = await self.delegate_task_to_worker(
                worker_role=SpecializedAgentRole.LEAVE_MANAGEMENT_AGENT,
                task_name="reconcile_unpaid_leaves",
                payload={"month": month},
            )

            # 3. Delegate payroll assistance prep
            pay_msg = await self.delegate_task_to_worker(
                worker_role=SpecializedAgentRole.PAYROLL_ASSISTANT_AGENT,
                task_name="prepare_payroll_staging_summary",
                payload={"month": month},
            )

            return {
                "operation": operation_name,
                "month": month,
                "status": "COMPLETED",
                "attendance_audit_msg_id": att_msg.message_id,
                "leave_audit_msg_id": leave_msg.message_id,
                "payroll_prep_msg_id": pay_msg.message_id,
            }

        return {"operation": operation_name, "status": "UNKNOWN_OPERATION"}
