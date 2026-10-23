"""
Agent Framework — Autonomy Levels.

AutonomyLevel controls how much independent decision-making an agent is
permitted to exercise. The level is configurable per agent, per action,
per department, and per organization.

Human authority is ALWAYS enforceable regardless of autonomy level.
"""

from __future__ import annotations

from enum import IntEnum


class AutonomyLevel(IntEnum):
    """
    Autonomy level scale for HRMS AI agents.

    Levels:
        LEVEL_0 — Human Only:
            The agent provides no recommendations.
            All decisions are made by humans.
            Example: Manual interview scheduling.

        LEVEL_1 — AI Recommends:
            Agent analyzes and presents recommendations.
            Humans make all final decisions.
            Example: Candidate ranking presented to HR manager.

        LEVEL_2 — AI Prepares, Human Approves:
            Agent prepares a complete action (draft email, payroll run).
            Human must explicitly approve before execution.
            Example: Candidate rejection email drafted, awaiting HR approval.

        LEVEL_3 — AI Executes Low-Risk Actions Automatically:
            Agent executes pre-approved, low-risk, reversible actions without
            per-action approval. High-risk actions still require approval.
            Example: Auto-schedule interviews for shortlisted candidates.

        LEVEL_4 — AI Executes Approved Classes of Actions Autonomously:
            Agent autonomously executes an approved category of actions
            with continuous monitoring. Anomalies trigger human escalation.
            Example: Resume parsing and initial screening runs fully autonomous.

        LEVEL_5 — Fully Autonomous (within governance boundaries):
            Agent operates independently within defined governance rules.
            All actions are monitored, logged, and auditable.
            Human can override at any time.
            Example: End-to-end recruitment pipeline for approved positions.
    """

    LEVEL_0 = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5

    @property
    def label(self) -> str:
        """Human-readable label for this autonomy level."""
        labels = {
            0: "Human Only",
            1: "AI Recommends",
            2: "AI Prepares, Human Approves",
            3: "AI Executes Low-Risk Autonomously",
            4: "AI Executes Approved Classes Autonomously",
            5: "Fully Autonomous (Governance Bounded)",
        }
        return labels[self.value]

    @property
    def allows_autonomous_execution(self) -> bool:
        """Return True if the agent may execute actions without per-action approval."""
        return self >= AutonomyLevel.LEVEL_3

    @property
    def requires_per_action_approval(self) -> bool:
        """Return True if every action requires explicit human approval."""
        return self <= AutonomyLevel.LEVEL_2

    def __str__(self) -> str:
        return f"LEVEL_{self.value} ({self.label})"
