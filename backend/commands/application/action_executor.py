"""
Action Executor — Decouples requested Command from executed runtime Action.
"""

from __future__ import annotations

from typing import Any

from backend.commands.application.handler import CommandHandler
from backend.commands.domain.models import Action, Command, CommandContext


class ActionExecutor:
    """
    Executes runtime Actions resolved from Commands.
    """

    async def execute_action(
        self,
        command: Command,
        handler: CommandHandler[Any],
        context: CommandContext,
    ) -> tuple[Action, dict[str, Any]]:
        """
        Create runtime Action representation and invoke Handler execution.
        """
        action = Action(
            action_type=f"act.{command.command_type}",
            command_id=command.command_id,
            target_resource_type=command.command_type.split(".")[0],
            target_resource_id=command.payload.get("id") or command.payload.get("employee_id") or "new",
            payload=command.payload,
        )

        result_data = await handler.execute(command, context)
        return action, result_data
