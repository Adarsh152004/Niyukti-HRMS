"""
Command Architecture — Command Parser interface.

The CommandParser converts raw channel input (natural language or structured)
into a typed Intent object. Concrete implementations (LLM-based, rule-based,
or hybrid) are provided in later nodes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.commands.contracts import Command, Intent, IntentCategory


class CommandParser(ABC):
    """
    Abstract command parser interface.

    Receives a Command with raw_input and populates the intent field.
    Parser implementations must be stateless and channel-agnostic.
    """

    @abstractmethod
    async def parse(self, command: Command) -> Intent:
        """
        Parse the raw_input of a command into a structured Intent.

        Args:
            command: The incoming Command object. Must have raw_input set.

        Returns:
            Populated Intent object. Sets intent.confidence to reflect certainty.

        Raises:
            ValueError: If the command has no raw_input.
        """
        ...

    @property
    @abstractmethod
    def parser_name(self) -> str:
        """Human-readable name of this parser implementation."""
        ...


class KeywordCommandParser(CommandParser):
    """
    Simple keyword-matching parser for testing and CLI use.

    Matches known command keywords to intents.
    Not suitable for natural-language commands — use LLM parser in production.
    """

    _KEYWORD_MAP: dict[str, tuple[IntentCategory, str]] = {
        "attrition": (IntentCategory.ANALYTICS, "predict_attrition"),
        "candidates": (IntentCategory.RECRUITMENT_QUERY, "list_candidates"),
        "screen": (IntentCategory.RECRUITMENT_ACTION, "screen_candidates"),
        "payroll": (IntentCategory.PAYROLL_QUERY, "view_payroll"),
        "performance": (IntentCategory.PERFORMANCE_QUERY, "view_performance"),
        "employees": (IntentCategory.EMPLOYEE_QUERY, "list_employees"),
        "report": (IntentCategory.REPORT, "generate_report"),
        "approve": (IntentCategory.APPROVAL_ACTION, "approve_request"),
        "reject": (IntentCategory.APPROVAL_ACTION, "reject_request"),
        "pause": (IntentCategory.AGENT_CONTROL, "pause_agent"),
        "resume": (IntentCategory.AGENT_CONTROL, "resume_agent"),
        "audit": (IntentCategory.AUDIT_QUERY, "view_audit_log"),
        "autonomy": (IntentCategory.AUTONOMY_CONTROL, "view_autonomy_status"),
    }

    @property
    def parser_name(self) -> str:
        return "keyword_parser_v1"

    async def parse(self, command: Command) -> Intent:
        from backend.commands.contracts import Intent, IntentCategory

        if not command.raw_input:
            raise ValueError("Command has no raw_input to parse.")

        raw_lower = command.raw_input.lower()
        for keyword, (category, action) in self._KEYWORD_MAP.items():
            if keyword in raw_lower:
                return Intent(
                    category=category,
                    action=action,
                    raw_text=command.raw_input,
                    confidence=0.75,
                )

        return Intent(
            category=IntentCategory.UNKNOWN,
            action="unknown",
            raw_text=command.raw_input,
            confidence=0.0,
        )
