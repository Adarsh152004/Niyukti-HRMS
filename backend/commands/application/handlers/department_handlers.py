"""
Department Command Handlers.
"""

from __future__ import annotations

from typing import Any

from backend.commands.application.handler import CommandHandler
from backend.commands.domain.models import Command, CommandContext


class CreateDepartmentCommandHandler(CommandHandler[Command]):
    """Handler for 'department.create' command."""

    async def execute(self, command: Command, context: CommandContext) -> dict[str, Any]:
        p = command.payload
        dept_id = p.get("department_id") or f"dept-{p.get('name', 'dept').lower()}"
        return {
            "department_id": dept_id,
            "name": p.get("name"),
            "organization_id": context.organization_id,
            "message": "Department created successfully via CommandBus.",
        }
