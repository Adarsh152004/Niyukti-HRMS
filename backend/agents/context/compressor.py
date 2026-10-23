"""
AI-Powered Intelligent HRMS — Conversation Context Compressor.
"""

from __future__ import annotations

from typing import Any


class ContextCompressor:
    """Sliding window compressor for conversation turns and observations."""

    def __init__(self, max_history_turns: int = 6) -> None:
        self.max_turns = max_history_turns

    def compress_history(self, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        if len(messages) <= self.max_turns:
            return messages

        # Preserve the very first prompt for intent anchoring, and last N turns
        first_msg = messages[0]
        recent = messages[-(self.max_turns - 1):]

        summary_notice = {
            "role": "system",
            "content": f"[Earlier conversation history ({len(messages) - self.max_turns} turns) compressed for brevity]",
        }
        return [first_msg, summary_notice] + recent
