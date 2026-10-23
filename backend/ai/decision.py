"""
AI Intelligence Layer — Decision Explainability contracts.

Every important AI decision must be explainable, auditable, and traceable.
Explainability records store concise, auditable reasoning — not raw chain-of-thought.

Fields align with the architecture specification:
- input_reference, decision, confidence, evidence, features/signals,
  reasoning_summary, model/version, agent, timestamp, policy_used,
  risk_score, human_override, final_outcome

IMPORTANT: Private LLM chain-of-thought is NEVER stored.
Only concise, human-readable decision summaries are persisted.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from backend.governance.risk import RiskLevel


class AIDecisionType(StrEnum):
    """Categories of AI decisions made by HRMS agents."""

    CANDIDATE_RANKING = "CANDIDATE_RANKING"
    RESUME_SCREENING = "RESUME_SCREENING"
    ATTRITION_PREDICTION = "ATTRITION_PREDICTION"
    PERFORMANCE_PREDICTION = "PERFORMANCE_PREDICTION"
    PROMOTION_READINESS = "PROMOTION_READINESS"
    SKILL_GAP_ANALYSIS = "SKILL_GAP_ANALYSIS"
    TRAINING_RECOMMENDATION = "TRAINING_RECOMMENDATION"
    SENTIMENT_ANALYSIS = "SENTIMENT_ANALYSIS"
    PAYROLL_ANOMALY_DETECTION = "PAYROLL_ANOMALY_DETECTION"
    WORKFORCE_PLANNING = "WORKFORCE_PLANNING"
    LEAVE_PATTERN_ANALYSIS = "LEAVE_PATTERN_ANALYSIS"
    CANDIDATE_REJECTION = "CANDIDATE_REJECTION"
    OTHER = "OTHER"


class AIDecision(BaseModel):
    """
    Explainable AI decision record.

    Stored for every significant AI decision. Used for:
    - Human review and override
    - Audit compliance
    - Model performance evaluation
    - HITL context

    Example (Candidate Ranking):
        decision:   "Candidate A ranked #1 of 12 applicants"
        confidence: 0.91
        evidence:   ["5 years relevant experience", "87% skill match",
                     "required certification present"]
        model:      "resume-ranking-v1"
        agent:      "candidate-ranking-agent"
    """

    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_type: AIDecisionType

    # Input reference (never the raw input — just a reference ID)
    input_reference_id: str = Field(description="ID of the input artifact (e.g. job_application_id, employee_id)")
    input_reference_type: str = Field(description="Type of the input (e.g. 'JobApplication', 'Employee')")

    # Core decision
    decision: str = Field(description="Human-readable statement of the decision made")
    confidence: float = Field(ge=0.0, le=1.0, description="Model confidence score [0, 1]")

    # Explainability
    evidence: list[str] = Field(
        default_factory=list,
        description="Concise evidence items supporting the decision (no raw PII)",
    )
    features_used: list[str] = Field(
        default_factory=list,
        description="Feature/signal names that influenced the decision",
    )
    reasoning_summary: str | None = Field(
        default=None,
        description=("Concise, auditable reasoning summary. " "NOT raw chain-of-thought. Max ~200 words."),
    )

    # Model provenance
    model_name: str = Field(description="Model or algorithm identifier, e.g. 'resume-ranking-v1'")
    model_version: str = Field(default="unknown")
    agent_id: str = Field(description="ID of the agent that made this decision")
    agent_role: str = Field(description="Role of the agent, e.g. 'candidate_ranking_agent'")

    # Risk and policy
    risk_level: RiskLevel = Field(default=RiskLevel.LOW)
    risk_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Numeric risk score (0 = no risk, 1 = maximum risk)",
    )
    policy_used: str | None = Field(
        default=None,
        description="Governance policy that governed this decision",
    )

    # Human override
    human_override: bool = Field(
        default=False,
        description="True if a human reviewer overrode this AI decision",
    )
    human_override_reason: str | None = Field(default=None)
    overridden_by: str | None = Field(default=None, description="ID of the human reviewer who overrode")
    overridden_at: datetime | None = Field(default=None)

    # Final outcome
    final_outcome: str | None = Field(
        default=None,
        description="What actually happened after HITL/override (may differ from AI decision)",
    )
    outcome_confirmed_at: datetime | None = Field(default=None)

    # Additional context
    metadata: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str | None = Field(default=None)

    # Timestamps
    decided_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    def apply_human_override(
        self,
        reviewer_id: str,
        reason: str,
        final_outcome: str,
    ) -> None:
        """Record a human override on this AI decision."""
        self.human_override = True
        self.human_override_reason = reason
        self.overridden_by = reviewer_id
        self.overridden_at = datetime.now(tz=UTC)
        self.final_outcome = final_outcome

    @property
    def is_high_confidence(self) -> bool:
        return self.confidence >= 0.85

    @property
    def needs_human_review(self) -> bool:
        return not self.is_high_confidence or self.risk_level.requires_human_approval

    def summary_dict(self) -> dict[str, Any]:
        """Return a concise non-PII summary suitable for API responses."""
        return {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type.value,
            "decision": self.decision,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "model": f"{self.model_name}@{self.model_version}",
            "agent_role": self.agent_role,
            "risk_level": self.risk_level.value,
            "human_override": self.human_override,
            "final_outcome": self.final_outcome,
            "decided_at": self.decided_at.isoformat(),
        }
