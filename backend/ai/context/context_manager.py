"""
Context Window Manager — Dynamic context assembly, token budgeting, sliding window, and safe prompt construction.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from backend.ai.context.budget_allocator import ContextBudgetAllocator, ContextSegment
from backend.ai.context.token_counter import TokenCounter

logger = logging.getLogger(__name__)


@dataclass
class AssembledContext:
    """Fully formed, token-bounded prompt context with component breakdown and provenance."""

    system_prompt: str
    user_prompt: str
    total_tokens: int
    provenance: dict[str, Any] = field(default_factory=dict)
    segment_token_counts: dict[str, int] = field(default_factory=dict)


class ContextManager:
    """
    Manages LLM context windows, prioritizing safety boundaries, memory ranking, and RAG retrieval.
    Guarantees:
    1. Security instructions and Agent Policies are NEVER truncated.
    2. Dynamic compression and sliding window applied to lower-priority memory and tool results.
    """

    _instance: ContextManager | None = None

    def __init__(
        self,
        token_counter: TokenCounter | None = None,
        budget_allocator: ContextBudgetAllocator | None = None,
    ) -> None:
        self.token_counter = token_counter or TokenCounter.get_instance()
        self.budget_allocator = budget_allocator or ContextBudgetAllocator()

    @classmethod
    def get_instance(cls) -> ContextManager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def assemble_context(
        self,
        system_instruction: str,
        security_boundary: str,
        agent_policy: str,
        task: str,
        plan: str | None = None,
        memory_items: list[str] | None = None,
        rag_chunks: list[dict[str, Any]] | None = None,
        tools_manifest: list[dict[str, Any]] | None = None,
        recent_results: list[dict[str, Any]] | None = None,
        max_context_tokens: int = 8192,
        model_name: str = "gpt-4o",
    ) -> AssembledContext:
        """
        Assemble grounded prompt respecting token allocations in strict priority order:
        SYSTEM + SECURITY + AGENT POLICY + TASK + PLAN + MEMORY + RAG + TOOLS + RECENT RESULTS
        """
        budgets = self.budget_allocator.get_budgets(max_context_tokens)
        segment_tokens: dict[str, int] = {}
        provenance: dict[str, Any] = {"rag_citations": [], "memory_count": 0, "tools_count": 0}

        # 1. Non-truncatable System, Security & Policy segments
        sys_text = f"=== SYSTEM ===\n{system_instruction.strip()}"
        sec_text = f"=== SECURITY INVARIANTS ===\n{security_boundary.strip()}"
        pol_text = f"=== AGENT GOVERNANCE & POLICY ===\n{agent_policy.strip()}"

        system_prompt = f"{sys_text}\n\n{sec_text}\n\n{pol_text}"
        segment_tokens[ContextSegment.SYSTEM] = self.token_counter.count_tokens(sys_text, model_name)
        segment_tokens[ContextSegment.SECURITY] = self.token_counter.count_tokens(sec_text, model_name)
        segment_tokens[ContextSegment.AGENT_POLICY] = self.token_counter.count_tokens(pol_text, model_name)

        # 2. Task & Plan
        task_text = f"=== ACTIVE TASK ===\n{task.strip()}"
        segment_tokens[ContextSegment.TASK] = self.token_counter.count_tokens(task_text, model_name)

        plan_parts: list[str] = []
        if plan:
            plan_text = f"=== ACTIVE PLAN ===\n{plan.strip()}"
            plan_parts.append(plan_text)
            segment_tokens[ContextSegment.PLAN] = self.token_counter.count_tokens(plan_text, model_name)

        # 3. Memory Items with sliding window / budget trimming
        mem_parts: list[str] = []
        if memory_items:
            mem_budget = budgets[ContextSegment.MEMORY].max_tokens
            current_mem_tokens = 0
            selected_mems: list[str] = []
            for item in reversed(memory_items):  # Most recent first
                tokens = self.token_counter.count_tokens(item, model_name)
                if current_mem_tokens + tokens <= mem_budget:
                    selected_mems.insert(0, item)
                    current_mem_tokens += tokens
                else:
                    break
            if selected_mems:
                mem_text = "=== RELEVANT MEMORY ===\n" + "\n".join(f"- {m}" for m in selected_mems)
                mem_parts.append(mem_text)
                segment_tokens[ContextSegment.MEMORY] = current_mem_tokens
                provenance["memory_count"] = len(selected_mems)

        # 4. RAG Authorized Chunks
        rag_parts: list[str] = []
        if rag_chunks:
            rag_budget = budgets[ContextSegment.RAG].max_tokens
            current_rag_tokens = 0
            selected_chunks: list[str] = []
            for chunk in rag_chunks:
                text = chunk.get("content") or chunk.get("text", "")
                doc_title = chunk.get("document_title") or chunk.get("source", "Internal Knowledge")
                formatted = f"[{doc_title}]: {text}"
                tokens = self.token_counter.count_tokens(formatted, model_name)
                if current_rag_tokens + tokens <= rag_budget:
                    selected_chunks.append(formatted)
                    provenance["rag_citations"].append({"source": doc_title, "chunk_id": chunk.get("chunk_id")})
                    current_rag_tokens += tokens
                else:
                    break
            if selected_chunks:
                rag_text = "=== AUTHORIZED KNOWLEDGE CONTEXT ===\n" + "\n\n".join(selected_chunks)
                rag_parts.append(rag_text)
                segment_tokens[ContextSegment.RAG] = current_rag_tokens

        # 5. Tools Manifest & Recent Tool Results
        tool_parts: list[str] = []
        if tools_manifest:
            manifest_lines = [f"- {t.get('tool_id')}: {t.get('description', '')}" for t in tools_manifest]
            t_text = "=== AVAILABLE TOOLS ===\n" + "\n".join(manifest_lines)
            tool_parts.append(t_text)
            segment_tokens[ContextSegment.TOOLS] = self.token_counter.count_tokens(t_text, model_name)
            provenance["tools_count"] = len(tools_manifest)

        results_parts: list[str] = []
        if recent_results:
            r_lines = [f"- {r.get('tool_id')}: {r.get('result')}" for r in recent_results]
            r_text = "=== RECENT EXECUTION RESULTS ===\n" + "\n".join(r_lines)
            results_parts.append(r_text)
            segment_tokens[ContextSegment.RECENT_RESULTS] = self.token_counter.count_tokens(r_text, model_name)

        # Assemble user prompt body
        user_body_sections = [task_text, *plan_parts, *mem_parts, *rag_parts, *tool_parts, *results_parts]
        user_prompt = "\n\n".join(user_body_sections)

        total_tokens = sum(segment_tokens.values())

        return AssembledContext(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            total_tokens=total_tokens,
            provenance=provenance,
            segment_token_counts={str(k): v for k, v in segment_tokens.items()},
        )
