"""
AI Gateway Telemetry — Cost attribution and business ROI measurement.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CostAttributionRecord(BaseModel):
    """Detailed attribution ledger entry for an LLM interaction."""

    attribution_id: str = Field(default_factory=lambda: f"cost-{uuid.uuid4()}")
    organization_id: str
    department_id: str | None = None
    agent_id: str | None = None
    task_id: str | None = None
    provider: str
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    latency_ms: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class AIROIMetrics(BaseModel):
    """Aggregated business return on investment indicators for AI features."""

    organization_id: str
    total_ai_spend_usd: float
    estimated_hours_saved: float
    estimated_cost_savings_usd: float
    recruiting_cycle_days_reduced: float
    hr_tickets_auto_resolved: int
    net_roi_ratio: float = Field(description="Savings / Spend ratio")
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class AITelemetryService:
    """Service tracking token spend attribution and calculating business ROI."""

    _instance: AITelemetryService | None = None

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._records: list[CostAttributionRecord] = []

    @classmethod
    def get_instance(cls) -> AITelemetryService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def record_usage(
        self,
        organization_id: str,
        provider: str,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
        latency_ms: int,
        department_id: str | None = None,
        agent_id: str | None = None,
        task_id: str | None = None,
    ) -> CostAttributionRecord:
        """Record an LLM usage event with organizational attribution."""
        record = CostAttributionRecord(
            organization_id=organization_id,
            department_id=department_id,
            agent_id=agent_id,
            task_id=task_id,
            provider=provider,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
        )

        async with self._lock:
            self._records.append(record)
            return record

    async def get_cost_summary(
        self,
        organization_id: str,
        department_id: str | None = None,
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        """Aggregate total token spend by organization, department, or agent."""
        async with self._lock:
            filtered = [
                r
                for r in self._records
                if r.organization_id == organization_id
                and (department_id is None or r.department_id == department_id)
                and (agent_id is None or r.agent_id == agent_id)
            ]

            total_spend = sum(r.cost_usd for r in filtered)
            total_tokens = sum(r.total_tokens for r in filtered)
            avg_latency = sum(r.latency_ms for r in filtered) / max(1, len(filtered))

            by_model: dict[str, float] = {}
            for r in filtered:
                by_model[r.model_name] = by_model.get(r.model_name, 0.0) + r.cost_usd

            return {
                "organization_id": organization_id,
                "total_spend_usd": round(total_spend, 4),
                "total_tokens": total_tokens,
                "average_latency_ms": round(avg_latency, 1),
                "spend_by_model": by_model,
                "call_count": len(filtered),
            }

    async def compute_roi(self, organization_id: str, hourly_rate_usd: float = 35.0) -> AIROIMetrics:
        """Compute organization AI return on investment."""
        summary = await self.get_cost_summary(organization_id)
        total_spend = summary["total_spend_usd"]
        call_count = summary["call_count"]

        # Approximate 5 minutes saved per autonomous/AI operation
        hours_saved = (call_count * 5.0) / 60.0
        cost_savings = hours_saved * hourly_rate_usd
        net_ratio = (cost_savings / total_spend) if total_spend > 0 else (cost_savings if cost_savings > 0 else 1.0)

        return AIROIMetrics(
            organization_id=organization_id,
            total_ai_spend_usd=total_spend,
            estimated_hours_saved=round(hours_saved, 1),
            estimated_cost_savings_usd=round(cost_savings, 2),
            recruiting_cycle_days_reduced=4.5,
            hr_tickets_auto_resolved=int(call_count * 0.4),
            net_roi_ratio=round(net_ratio, 2),
        )
