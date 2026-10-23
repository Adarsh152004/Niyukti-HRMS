"""
Tests for Model Registry, Shadow Mode, Canary Releases, and Rollback.
"""

from __future__ import annotations

import pytest

from backend.ml.domain.enums import ModelStage
from backend.ml.domain.models import ModelVersion
from backend.ml.registry.model_registry import ModelRegistryService


@pytest.mark.asyncio
async def test_model_lifecycle_shadow_canary_active_and_rollback():
    reg = ModelRegistryService.get_instance()
    org_id = "org-release-test"

    # 1. Register logical model
    model = await reg.register_model(org_id, name="WorkforceForecaster")
    assert model.stage == ModelStage.DEVELOPMENT

    # 2. Save version 1 and activate
    v1 = ModelVersion(
        model_id=model.model_id,
        organization_id=org_id,
        version_number=1,
        algorithm="LinearRegression",
        dataset_version_id="dsv-1",
        feature_set_version="1.0",
        storage_reference="ref1",
        stage=ModelStage.DEVELOPMENT,
    )
    await reg.store.save_version(v1)
    await reg.release_service.activate_model(org_id, model.model_id, v1.version_id, approved_by="admin-1")

    m_active = await reg.get_model(org_id, model.model_id)
    assert m_active.active_version_id == v1.version_id
    assert m_active.stage == ModelStage.ACTIVE

    # 3. Save version 2 and promote to SHADOW
    v2 = ModelVersion(
        model_id=model.model_id,
        organization_id=org_id,
        version_number=2,
        algorithm="RandomForest",
        dataset_version_id="dsv-2",
        feature_set_version="2.0",
        storage_reference="ref2",
        stage=ModelStage.DEVELOPMENT,
    )
    await reg.store.save_version(v2)
    await reg.release_service.promote_to_shadow(org_id, model.model_id, v2.version_id)

    m_shadow = await reg.get_model(org_id, model.model_id)
    assert m_shadow.shadow_version_id == v2.version_id
    # Active version remains unchanged
    assert m_shadow.active_version_id == v1.version_id

    # 4. Promote version 2 to CANARY (20% traffic)
    await reg.release_service.promote_to_canary(org_id, model.model_id, v2.version_id, traffic_percent=20.0)
    m_canary = await reg.get_model(org_id, model.model_id)
    assert m_canary.canary_version_id == v2.version_id
    assert m_canary.canary_traffic_percent == 20.0

    # 5. Activate version 2 (Full rollout)
    await reg.release_service.activate_model(org_id, model.model_id, v2.version_id, approved_by="admin-1")
    m_v2_active = await reg.get_model(org_id, model.model_id)
    assert m_v2_active.active_version_id == v2.version_id
    assert m_v2_active.rollback_target_version_id == v1.version_id
    assert m_v2_active.canary_version_id is None

    # 6. Rollback to version 1
    await reg.rollback_service.rollback_model(org_id, model.model_id, reason="Drift detected", operator_id="admin-1")
    m_rolled = await reg.get_model(org_id, model.model_id)
    assert m_rolled.active_version_id == v1.version_id
