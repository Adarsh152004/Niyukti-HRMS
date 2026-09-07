"""
Saga Compensation Registry — Maps forward mutating commands to inverse compensating commands.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class CompensationRegistry:
    """
    Registry for Saga compensation handlers.
    Provides inverse actions for rollback when distributed multi-step workflows encounter unrecoverable errors.
    """

    _instance: CompensationRegistry | None = None

    def __init__(self) -> None:
        self._compensations: dict[str, str] = {
            "employee.create": "employee.terminate",
            "department.create": "department.delete",
            "leave.deduct_balance": "leave.restore_balance",
            "payroll.stage_run": "payroll.cancel_run",
            "it.provision_account": "it.revoke_account",
            "asset.assign_laptop": "asset.unassign_laptop",
            "course.enroll": "course.unenroll",
            "salary.revise": "salary.rollback_revision",
        }

    @classmethod
    def get_instance(cls) -> CompensationRegistry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_compensation(self, forward_command_type: str, compensating_command_type: str) -> None:
        self._compensations[forward_command_type] = compensating_command_type

    def get_compensating_command(self, forward_command_type: str) -> str | None:
        return self._compensations.get(forward_command_type)
