"""
Command Registry — Central registry for handler lookup, metadata discovery, and AI tool registries.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from backend.commands.application.handler import CommandHandler
from backend.commands.domain.models import CommandMetadata


class CommandAlreadyRegisteredError(Exception):
    """Raised when a command type is registered more than once."""

    pass


class CommandNotRegisteredError(Exception):
    """Raised when looking up an unregistered command type."""

    pass


class CommandRegistry:
    """
    Extensible registry holding command handlers and metadata.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, CommandHandler[Any]] = {}
        self._metadata: dict[str, CommandMetadata] = {}

    def register(
        self,
        command_type: str,
        handler: CommandHandler[Any],
        metadata: CommandMetadata,
    ) -> None:
        """
        Register a command type, handler, and metadata.
        Prevents duplicate registrations.
        """
        if command_type in self._handlers:
            raise CommandAlreadyRegisteredError(f"Command type '{command_type}' is already registered in registry.")
        self._handlers[command_type] = handler
        self._metadata[command_type] = metadata

    def get_handler(self, command_type: str) -> CommandHandler[Any]:
        """Resolve handler for a command type."""
        handler = self._handlers.get(command_type)
        if not handler:
            raise CommandNotRegisteredError(f"No handler registered for command type '{command_type}'.")
        return handler

    def get_metadata(self, command_type: str) -> CommandMetadata:
        """Resolve metadata schema for a command type."""
        meta = self._metadata.get(command_type)
        if not meta:
            raise CommandNotRegisteredError(f"No metadata registered for command type '{command_type}'.")
        return meta

    def list_commands(self) -> Sequence[CommandMetadata]:
        """List metadata for all registered commands (for AI tool discovery)."""
        return list(self._metadata.values())
