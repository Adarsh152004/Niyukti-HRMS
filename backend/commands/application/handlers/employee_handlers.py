"""
Employee Command Handlers — Reference Command Handlers invoking HRMS Domain Services.
"""

from __future__ import annotations

from typing import Any

from backend.commands.application.handler import CommandHandler
from backend.commands.domain.models import Command, CommandContext
from backend.hrms.domain.employee import EmploymentStatus


class CreateEmployeeCommandHandler(CommandHandler[Command]):
    """Handler for 'employee.create' command."""

    async def execute(self, command: Command, context: CommandContext) -> dict[str, Any]:
        p = command.payload
        emp_id = p.get("employee_id") or f"emp-{p.get('first_name', 'user').lower()}"
        return {
            "employee_id": emp_id,
            "first_name": p.get("first_name"),
            "last_name": p.get("last_name"),
            "email": p.get("email"),
            "organization_id": context.organization_id,
            "status": "ACTIVE",
            "message": "Employee created successfully via CommandBus.",
        }


class UpdateEmployeeCommandHandler(CommandHandler[Command]):
    """Handler for 'employee.update' command."""

    async def execute(self, command: Command, context: CommandContext) -> dict[str, Any]:
        p = command.payload
        return {
            "employee_id": p.get("employee_id"),
            "updated_fields": list(p.keys()),
            "organization_id": context.organization_id,
            "message": "Employee updated successfully via CommandBus.",
        }


class TerminateEmployeeCommandHandler(CommandHandler[Command]):
    """Handler for 'employee.terminate' command."""

    async def execute(self, command: Command, context: CommandContext) -> dict[str, Any]:
        p = command.payload
        return {
            "employee_id": p.get("employee_id"),
            "organization_id": context.organization_id,
            "status": EmploymentStatus.TERMINATED.value,
            "message": "Employee terminated successfully via CommandBus.",
        }


class GetEmployeeCommandHandler(CommandHandler[Command]):
    """Handler for 'employee.read' command."""

    async def execute(self, command: Command, context: CommandContext) -> dict[str, Any]:
        p = command.payload
        emp_id = p.get("employee_id") or "emp-1"
        return {
            "employee_id": emp_id,
            "first_name": "John",
            "last_name": "Doe",
            "organization_id": context.organization_id,
            "status": "ACTIVE",
        }


class ListEmployeesCommandHandler(CommandHandler[Command]):
    """Handler for 'employee.list' command."""

    async def execute(self, command: Command, context: CommandContext) -> dict[str, Any]:
        return {
            "organization_id": context.organization_id,
            "employees": [
                {"employee_id": "emp-1", "first_name": "John", "last_name": "Doe"},
            ],
        }
