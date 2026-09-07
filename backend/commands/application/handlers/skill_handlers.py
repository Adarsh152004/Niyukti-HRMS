"""
Skill Command Handlers.
"""

from __future__ import annotations

from typing import Any

from backend.commands.application.handler import CommandHandler
from backend.commands.domain.models import Command, CommandContext


class CreateSkillCommandHandler(CommandHandler[Command]):
    """Handler for 'skill.create' command."""

    async def execute(self, command: Command, context: CommandContext) -> dict[str, Any]:
        p = command.payload
        skill_id = p.get("skill_id") or f"skill-{p.get('name', 'skill').lower()}"
        return {
            "skill_id": skill_id,
            "name": p.get("name"),
            "category": p.get("category", "General"),
            "organization_id": context.organization_id,
            "message": "Skill created successfully via CommandBus.",
        }
