"""
Platform Command Line Interface (CLI) Foundation.

Provides command list, inspect, execute, and status CLI capabilities.
Calls the exact same CommandBus pipeline as Web and API channels.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from backend.commands.api.router import get_command_bus
from backend.commands.application.bus import CommandBus
from backend.commands.domain.enums import CommandChannel
from backend.commands.domain.models import Command, CommandMetadata, CommandResult
from backend.hrms.domain.actor import Actor


class PlatformCLI:
    """
    CLI interface executing commands through universal CommandBus.
    """

    def __init__(self, bus: CommandBus | None = None) -> None:
        self.bus = bus or get_command_bus()

    def list_commands(self) -> Sequence[CommandMetadata]:
        """List all available commands in registry."""
        return self.bus.registry.list_commands()

    def inspect_command(self, command_type: str) -> CommandMetadata:
        """Inspect metadata for a specific command."""
        return self.bus.registry.get_metadata(command_type)

    async def execute_command(
        self,
        command_type: str,
        payload: dict[str, Any],
        actor: Actor,
        idempotency_key: str | None = None,
    ) -> CommandResult:
        """
        Execute a command from CLI channel.
        """
        cmd = Command(
            command_type=command_type,
            actor_id=actor.actor_id,
            organization_id=actor.organization_id,
            channel=CommandChannel.CLI,
            payload=payload,
            idempotency_key=idempotency_key,
        )
        context = self.bus.build_context(actor=actor, channel=CommandChannel.CLI)
        return await self.bus.dispatch(cmd, context)

    def get_status(self, command_id: str) -> str:
        """Inspect status of a command by ID."""
        cmd = self.bus._history.get(command_id)
        if not cmd:
            return "NOT_FOUND"
        return cmd.status.value
