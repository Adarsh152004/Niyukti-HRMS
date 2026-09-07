"""
Command Handler Interface — Abstract base class for all application command handlers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from backend.commands.domain.models import Command, CommandContext

TCommand = TypeVar("TCommand", bound=Command)


class CommandHandler(ABC, Generic[TCommand]):
    """
    Abstract base class for Command Handlers.
    Handlers execute application logic via domain/application services.
    """

    @abstractmethod
    async def execute(self, command: TCommand, context: CommandContext) -> dict[str, Any]:
        """
        Execute the command within trusted execution context.
        Returns result data dictionary.
        """
        pass
