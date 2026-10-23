"""
Planner — Helper module for decomposing high-level agent goals into sub-goals.
"""

from __future__ import annotations

from backend.agents.domain.models import AgentTask


class Planner:
    """
    Decomposes AgentTask goals into manageable sub-goals.
    """

    @staticmethod
    def create_plan_summary(task: AgentTask) -> str:
        return f"Plan for task '{task.task_id}': Achieve goal '{task.goal}' with priority {task.priority.value}."
