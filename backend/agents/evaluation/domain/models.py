"""
Evaluation Domain Models — EvaluationResult and criteria evaluation models.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


def generate_eval_id() -> str:
    return f"eval-{uuid.uuid4()}"


class EvaluationResult(BaseModel):
    """
    Structured result of a trajectory or agent behavioral evaluation.
    """

    evaluation_id: str = Field(default_factory=generate_eval_id)
    organization_id: str
    agent_id: str
    task_id: str
    evaluator: str = Field(default="TraceEvaluator")
    score: float = Field(default=1.0, ge=0.0, le=1.0, description="Score between 0.0 and 1.0")
    passed: bool = Field(default=True)
    criteria_evaluated: list[str] = Field(default_factory=list)
    failures: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)
