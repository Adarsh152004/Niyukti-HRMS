"""Tests — Metrics Service Recording & Aggregation."""

import pytest

from backend.agents.governance.application.metrics_service import MetricsService


@pytest.mark.asyncio
async def test_metrics_recording_and_summary():
    svc = MetricsService()

    await svc.record_metric("org-acme", "tasks_total", 1.0, agent_id="bot-metrics")
    await svc.record_metric("org-acme", "tasks_success", 1.0, agent_id="bot-metrics")
    await svc.record_metric("org-acme", "commands_total", 5.0, agent_id="bot-metrics")

    summary = await svc.get_metrics_summary("org-acme", agent_id="bot-metrics")
    assert summary["metrics"]["tasks_total"] == 1.0
    assert summary["metrics"]["tasks_success"] == 1.0
    assert summary["metrics"]["commands_total"] == 5.0
