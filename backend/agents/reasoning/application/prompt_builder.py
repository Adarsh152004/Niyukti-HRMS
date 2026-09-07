"""
Prompt Builder — Constructs deterministic system and task prompts without exposing credentials.
"""

from __future__ import annotations

from backend.agents.memory.application.context_builder import BoundedContext


class PromptBuilder:
    """
    Constructs deterministic prompt payloads for LLM reasoning providers.
    """

    @staticmethod
    def build_system_prompt(ctx: BoundedContext) -> str:
        tools_str = (
            "\n".join([f"- {t['tool_id']}: {t['description']} (Risk: {t['risk_level']})" for t in ctx.allowed_tools]) or "None"
        )

        caps_str = ", ".join(ctx.capabilities) or "None"
        memories_str = "\n".join([f"- {m}" for m in ctx.memories]) or "None"

        return f"""You are AI Agent '{ctx.agent_name}' ({ctx.agent_type}) operating within Tenant Organization '{ctx.organization_id}'.

STRICT SECURITY INVARIANTS:
1. You MUST NOT modify enterprise state directly. State mutations MUST be proposed via authorized tools.
2. You MUST NOT escalate capabilities beyond your declared set: [{caps_str}].
3. You MUST NOT cross tenant boundaries or access unauthorized resources.
4. You MUST NOT bypass Human-In-The-Loop (HITL) approval requirements.
5. Output MUST be valid JSON conforming to ReasoningDecision schema.

AVAILABLE CAPABILITIES:
{caps_str}

AVAILABLE DISCOVERED TOOLS:
{tools_str}

RELEVANT RECENT MEMORIES:
{memories_str}
"""

    @staticmethod
    def build_user_prompt(ctx: BoundedContext) -> str:
        results_str = (
            "\n".join(
                [f"- Tool {r['tool_id']}: Status={r['status']}, Data={r['data']}, Error={r['error']}" for r in ctx.tool_results]
            )
            or "No previous tool executions."
        )

        return f"""TASK OBJECTIVE: {ctx.task_goal}
TASK INPUT: {ctx.task_input}

PREVIOUS STEP RESULTS:
{results_str}

Current Step: {ctx.step_number}. Provide your next ReasoningDecision JSON.
"""
