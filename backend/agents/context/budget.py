"""
AI-Powered Intelligent HRMS — Context Window Token Budgeting Engine.

Allocates explicit token allowances across:
- System Instructions
- Long-Term & Episodic Memory
- RAG Document Retrieval Citations
- Governed Tool Execution Results
- User Input Prompt
- Output Generation Allowance
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TokenBudgetAllocation:
    max_total_tokens: int = 8192
    system_instruction_limit: int = 1500
    memory_limit: int = 1000
    rag_retrieval_limit: int = 2000
    tool_results_limit: int = 2000
    user_prompt_limit: int = 1000
    reserved_output_tokens: int = 1500


@dataclass
class TokenUsageBreakdown:
    system_tokens: int = 0
    memory_tokens: int = 0
    rag_tokens: int = 0
    tool_tokens: int = 0
    user_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_consumed(self) -> int:
        return (
            self.system_tokens
            + self.memory_tokens
            + self.rag_tokens
            + self.tool_tokens
            + self.user_tokens
            + self.output_tokens
        )


class ContextBudgetManager:
    """Manages token budgets and trims context components to prevent model context overflow."""

    def __init__(self, allocation: TokenBudgetAllocation | None = None) -> None:
        self.allocation = allocation or TokenBudgetAllocation()

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Heuristic estimation: ~4 chars per token."""
        return max(1, len(text) // 4)

    def truncate_to_token_limit(self, text: str, max_tokens: int) -> str:
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "\n... [Context truncated to fit token budget]"

    def assemble_budgeted_context(
        self,
        system_prompt: str,
        user_prompt: str,
        memories: list[str] | None = None,
        rag_chunks: list[str] | None = None,
        tool_results: list[dict[str, Any]] | None = None,
    ) -> tuple[dict[str, Any], TokenUsageBreakdown]:
        """Assembles prompt components strictly within token limits."""
        usage = TokenUsageBreakdown()

        # 1. System Prompt
        clean_system = self.truncate_to_token_limit(
            system_prompt, self.allocation.system_instruction_limit
        )
        usage.system_tokens = self.estimate_tokens(clean_system)

        # 2. User Prompt
        clean_user = self.truncate_to_token_limit(
            user_prompt, self.allocation.user_prompt_limit
        )
        usage.user_tokens = self.estimate_tokens(clean_user)

        # 3. Memories
        memory_str = "\n".join(memories or [])
        clean_memory = self.truncate_to_token_limit(
            memory_str, self.allocation.memory_limit
        )
        usage.memory_tokens = self.estimate_tokens(clean_memory)

        # 4. RAG Chunks
        rag_str = "\n---\n".join(rag_chunks or [])
        clean_rag = self.truncate_to_token_limit(
            rag_str, self.allocation.rag_retrieval_limit
        )
        usage.rag_tokens = self.estimate_tokens(clean_rag)

        # 5. Tool Results
        import json
        tool_str = json.dumps(tool_results or [])
        clean_tools = self.truncate_to_token_limit(
            tool_str, self.allocation.tool_results_limit
        )
        usage.tool_tokens = self.estimate_tokens(clean_tools)

        context = {
            "system_prompt": clean_system,
            "user_prompt": clean_user,
            "memories": clean_memory,
            "rag_context": clean_rag,
            "tool_results": clean_tools,
        }

        return context, usage
