"""
Standard HR Model Service Templates — High-level facades for domain intelligence models.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from backend.ml.domain.models import PredictionRequest
from backend.ml.inference.prediction_service import PredictionService


class AttritionRiskOutput(BaseModel):
    risk_level: str  # "LOW", "MEDIUM", "HIGH"
    risk_probability: float
    confidence: float
    abstain: bool
    top_factors: list[str] = Field(default_factory=list)


class PerformanceForecastOutput(BaseModel):
    projected_rating: float
    confidence: float
    trend: str  # "IMPROVING", "STABLE", "DECLINING"
    abstain: bool


class WorkforceForecastOutput(BaseModel):
    projected_headcount_need: int
    confidence: float
    horizon_months: int


class CandidateRankingOutput(BaseModel):
    candidate_id: str
    rank_score: float
    skill_match_rate: float
    confidence: float
    abstain: bool


class SkillGapOutput(BaseModel):
    missing_critical_skills: list[str]
    gap_severity: str  # "LOW", "MODERATE", "CRITICAL"
    confidence: float


class SentimentClassificationOutput(BaseModel):
    sentiment: str  # "POSITIVE", "NEUTRAL", "NEGATIVE"
    confidence: float
    urgency_level: str


class HRAnomalyOutput(BaseModel):
    is_anomaly: bool
    anomaly_score: float
    severity: str
    anomaly_reason: str


class AttritionPredictor:
    """HR Intelligence template for Employee Attrition Risk Forecasting."""

    def __init__(self, prediction_service: PredictionService | None = None) -> None:
        self.service = prediction_service or PredictionService.get_instance()

    async def predict_attrition(
        self,
        organization_id: str,
        employee_id: str,
        actor_id: str,
        actor_roles: list[str],
        features: dict[str, Any],
    ) -> AttritionRiskOutput:
        req = PredictionRequest(
            organization_id=organization_id,
            model_id="attrition-risk-model",
            actor_id=actor_id,
            actor_roles=actor_roles,
            entity_id=employee_id,
            input_features=features,
        )
        res = await self.service.predict(req)

        if res.decision != res.decision.PREDICT or res.probability is None:
            return AttritionRiskOutput(
                risk_level="UNKNOWN",
                risk_probability=0.0,
                confidence=0.0,
                abstain=True,
                top_factors=[res.abstain_reason or "Abstained"],
            )

        prob = res.probability
        level = "HIGH" if prob >= 0.70 else "MEDIUM" if prob >= 0.40 else "LOW"
        factors: list[str] = []
        if features.get("leave_frequency_90d", 0) > 10:
            factors.append("High leave frequency in past 90 days")
        if features.get("engagement_score", 100) < 40:
            factors.append("Low pulse engagement survey score")

        return AttritionRiskOutput(
            risk_level=level,
            risk_probability=prob,
            confidence=res.confidence,
            abstain=False,
            top_factors=factors,
        )
