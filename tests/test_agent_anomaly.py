"""Tests — Anomaly Service Evidence Recording & Retrieval."""

import pytest

from backend.agents.governance.application.anomaly_service import AnomalyService
from backend.agents.governance.domain.enums import AnomalyType, Severity


@pytest.mark.asyncio
async def test_anomaly_detection_recording():
    svc = AnomalyService()

    anomaly = await svc.detect_and_record_anomaly(
        organization_id="org-acme",
        agent_id="bot-anomaly",
        anomaly_type=AnomalyType.CAPABILITY_BOUNDARY_ATTEMPT,
        severity=Severity.HIGH,
        evidence={"attempted_resource": "payroll", "action": "delete"},
    )

    assert anomaly.anomaly_type == AnomalyType.CAPABILITY_BOUNDARY_ATTEMPT
    assert anomaly.severity == Severity.HIGH
    assert anomaly.evidence["attempted_resource"] == "payroll"

    anomalies = await svc.list_anomalies("org-acme", "bot-anomaly")
    assert len(anomalies) == 1
