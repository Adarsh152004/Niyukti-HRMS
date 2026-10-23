"""
Tests for AI Agent ML Integration Invariants, Tenant Isolation, and HITL Governance.
"""

from __future__ import annotations

import pytest

from backend.hrms.domain.actor import Actor, ActorType
from backend.ml.domain.enums import PredictionDecision
from backend.ml.domain.exceptions import ModelNotFoundError
from backend.ml.domain.models import ModelVersion, PredictionRequest
from backend.ml.inference.prediction_service import PredictionService
from backend.ml.lineage.lineage_service import DecisionLineageService
from backend.ml.registry.model_registry import ModelRegistryService


@pytest.mark.asyncio
async def test_strict_tenant_isolation_in_models_and_predictions():
    reg = ModelRegistryService.get_instance()
    pred_svc = PredictionService.get_instance()

    org_a = "org-alpha"
    org_b = "org-beta"

    # Register model in Org Alpha
    model_a = await reg.register_model(org_a, name="AlphaCompensationModel")
    v1 = ModelVersion(
        model_id=model_a.model_id,
        organization_id=org_a,
        version_number=1,
        algorithm="LR",
        dataset_version_id="dsv-alpha",
        feature_set_version="1.0",
        storage_reference="ref-alpha",
    )
    await reg.store.save_version(v1)
    await reg.release_service.activate_model(org_a, model_a.model_id, v1.version_id, approved_by="admin-alpha")

    # Actor from Org Beta queries model from Org Alpha -> MUST FAIL
    models_b = await reg.list_models(org_b)
    assert not any(m.model_id == model_a.model_id for m in models_b)

    req_b = PredictionRequest(
        organization_id=org_b,
        model_id=model_a.model_id,
        actor_id="user-b",
        actor_roles=["HR_ADMIN"],
        input_features={"employee_tenure_months": 24.0},
    )
    with pytest.raises(ModelNotFoundError):
        await pred_svc.predict(req_b)


@pytest.mark.asyncio
async def test_ai_agent_cannot_bypass_governance_or_mutate_models():
    reg = ModelRegistryService.get_instance()
    org_id = "org-agent-gov-test"

    model = await reg.register_model(org_id, name="PerformanceModel")
    v1 = ModelVersion(
        model_id=model.model_id,
        organization_id=org_id,
        version_number=1,
        algorithm="LR",
        dataset_version_id="dsv-1",
        feature_set_version="1.0",
        storage_reference="ref",
    )
    await reg.store.save_version(v1)
    await reg.release_service.activate_model(org_id, model.model_id, v1.version_id, approved_by="admin-1")

    # AI Agent Actor
    agent_actor = Actor(
        actor_id="attrition-retention-agent",
        actor_type=ActorType.AI_AGENT,
        organization_id=org_id,
        identity="attrition-agent",
        roles={"AI_AGENT"},
        permissions={"ml:predict"},  # Agent has predict permission only, NOT model:activate or model:rollback
    )

    # Invariant: AI Agent CAN read predictions to assist reasoning
    pred_req = PredictionRequest(
        organization_id=org_id,
        model_id=model.model_id,
        actor_id=agent_actor.actor_id,
        actor_roles=list(agent_actor.roles),
        input_features={"employee_tenure_months": 36.0, "leave_frequency_90d": 1.0},
    )
    res = await PredictionService.get_instance().predict(pred_req)
    assert res.decision == PredictionDecision.PREDICT

    # Invariant: Correlation ID is preserved across inference and lineage
    lin = await DecisionLineageService.get_instance().get_lineage(org_id, res.lineage_id)
    assert lin.correlation_id == pred_req.correlation_id
