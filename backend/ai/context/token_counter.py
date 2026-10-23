"""
Token Counter — Model-aware token estimation and accounting.
"""

from __future__ import annotations

import re


class TokenCounter:
    """Estimates and counts token lengths across various LLM model families."""

    _instance: TokenCounter | None = None

    @classmethod
    def get_instance(cls) -> TokenCounter:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def count_tokens(self, text: str, model_name: str = "gpt-4o") -> int:
        """
        Estimate token count using fast heuristic character/word ratios with special token weighting.
        """
        if not text:
            return 0

        # Heuristic calculation: ~4 characters per token for English text, with overhead for punctuation/code
        words = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
        estimated = int(len(words) * 1.15)
        return max(1, estimated)

    def count_messages_tokens(self, messages: list[dict[str, str]], model_name: str = "gpt-4o") -> int:
        """Calculate total tokens across chat messages including envelope overhead."""
        total = 0
        for msg in messages:
            total += 4  # Message envelope tokens
            for _k, v in msg.items():
                total += self.count_tokens(v, model_name=model_name)
        total += 3  # Conversation ending token overhead
        return total
