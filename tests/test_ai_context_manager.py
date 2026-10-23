"""
Tests for Context Window Manager, Token Accounting, and Safety Instruction Immutability.
"""

from __future__ import annotations

from backend.ai.context.context_manager import ContextManager


def test_context_manager_assembly_and_priority():
    ctx_mgr = ContextManager.get_instance()

    sys_instr = "You are the Executive HR Agent."
    sec_bound = "INVARIANT: LLM cannot perform direct salary alterations without human approval."
    pol = "POLICY: Limit queries to authorized organization scope."
    task = "Prepare executive headcount report."

    memories = [f"Past conversation item {i}" for i in range(20)]
    rag_chunks = [
        {"document_title": "Leave Policy 2026", "content": "Paid leaves are accrued at 1.66 days/month.", "chunk_id": "c1"},
        {"document_title": "Remote Work SOP", "content": "Employees may work remotely up to 2 days/week.", "chunk_id": "c2"},
    ]
    tools = [{"tool_id": "analytics.get_headcount_stats", "description": "Returns employee counts."}]

    assembled = ctx_mgr.assemble_context(
        system_instruction=sys_instr,
        security_boundary=sec_bound,
        agent_policy=pol,
        task=task,
        memory_items=memories,
        rag_chunks=rag_chunks,
        tools_manifest=tools,
        max_context_tokens=4096,
    )

    # 1. Invariant: Security invariants and policies MUST be present in system prompt
    assert sec_bound in assembled.system_prompt
    assert pol in assembled.system_prompt
    assert sys_instr in assembled.system_prompt

    # 2. Invariant: RAG citations and provenance are preserved
    assert len(assembled.provenance["rag_citations"]) == 2
    assert "Leave Policy 2026" in assembled.user_prompt
    assert "analytics.get_headcount_stats" in assembled.user_prompt

    # 3. Token counts accounted
    assert assembled.total_tokens > 50
    assert "SYSTEM" in assembled.segment_token_counts
    assert "SECURITY" in assembled.segment_token_counts
