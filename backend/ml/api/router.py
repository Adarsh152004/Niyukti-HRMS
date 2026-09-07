"""
ML API Router — REST endpoints for predictive inferences, model catalog, shadow/canary deployments, rollback, and decision lineage.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.hrms.domain.actor import Actor
from backend.ml.domain.enums import ModelStage
from backend.ml.domain.models import (
    ModelDefinition,
    ModelVersion,
    PredictionLineage,
    PredictionRequest,
    PredictionResult,
)
from backend.ml.inference.prediction_service import PredictionService
from backend.ml.lineage.lineage_service import DecisionLineageService
from backend.ml.registry.model_registry import ModelRegistryService
from backend.security.api.dependencies import get_current_actor

router = APIRouter(prefix="/api/v1/ml", tags=["Predictive ML Platform"])


class InferenceAPIRequest(BaseModel):
    model_id: str
    input_features: dict[str, Any]
    entity_id: str | None = None


class PromoteShadowRequest(BaseModel):
    version_id: str


class PromoteCanaryRequest(BaseModel):
    version_id: str
    traffic_percent: float = Field(default=10.0, ge=0.0, le=100.0)


class ActivateModelRequest(BaseModel):
    version_id: str


class RollbackModelRequest(BaseModel):
    reason: str


# ── Inference Endpoints ────────────────────────────────────────────────────────


@router.post("/predict", response_model=PredictionResult)
async def predict_endpoint(
    req: InferenceAPIRequest,
    actor: Actor = Depends(get_current_actor),
) -> PredictionResult:
    service = PredictionService.get_instance()
    pred_req = PredictionRequest(
        organization_id=actor.organization_id,
        model_id=req.model_id,
        actor_id=actor.actor_id,
        actor_roles=list(actor.roles),
        input_features=req.input_features,
        entity_id=req.entity_id,
    )
    return await service.predict(pred_req)


# ── Model Registry & Lifecycle Endpoints ──────────────────────────────────────


@router.get("/models", response_model=Sequence[ModelDefinition])
async def list_models(
    stage: ModelStage | None = None,
    actor: Actor = Depends(get_current_actor),
) -> Sequence[ModelDefinition]:
    reg = ModelRegistryService.get_instance()
    return await reg.list_models(actor.organization_id, stage=stage)


@router.get("/models/{model_id}", response_model=ModelDefinition)
async def get_model(
    model_id: str,
    actor: Actor = Depends(get_current_actor),
) -> ModelDefinition:
    reg = ModelRegistryService.get_instance()
    m = await reg.get_model(actor.organization_id, model_id)
    if not m:
        raise HTTPException(status_code=404, detail="Model not found.")
    return m


@router.get("/models/{model_id}/versions", response_model=Sequence[ModelVersion])
async def list_model_versions(
    model_id: str,
    actor: Actor = Depends(get_current_actor),
) -> Sequence[ModelVersion]:
    reg = ModelRegistryService.get_instance()
    return await reg.list_model_versions(actor.organization_id, model_id)


@router.get("/models/{model_id}/lineage", response_model=Sequence[PredictionLineage])
async def list_model_lineage(
    model_id: str,
    limit: int = 50,
    actor: Actor = Depends(get_current_actor),
) -> Sequence[PredictionLineage]:
    lin_svc = DecisionLineageService.get_instance()
    return await lin_svc.list_model_lineages(actor.organization_id, model_id, limit=limit)


# ── Governance & Release Endpoints ────────────────────────────────────────────


@router.post("/models/{model_id}/shadow", response_model=ModelDefinition)
async def promote_to_shadow(
    model_id: str,
    req: PromoteShadowRequest,
    actor: Actor = Depends(get_current_actor),
) -> ModelDefinition:
    reg = ModelRegistryService.get_instance()
    return await reg.release_service.promote_to_shadow(actor.organization_id, model_id, req.version_id)


@router.post("/models/{model_id}/canary", response_model=ModelDefinition)
async def promote_to_canary(
    model_id: str,
    req: PromoteCanaryRequest,
    actor: Actor = Depends(get_current_actor),
) -> ModelDefinition:
    reg = ModelRegistryService.get_instance()
    return await reg.release_service.promote_to_canary(
        actor.organization_id, model_id, req.version_id, traffic_percent=req.traffic_percent
    )


@router.post("/models/{model_id}/activate", response_model=ModelDefinition)
async def activate_model(
    model_id: str,
    req: ActivateModelRequest,
    actor: Actor = Depends(get_current_actor),
) -> ModelDefinition:
    reg = ModelRegistryService.get_instance()
    return await reg.release_service.activate_model(actor.organization_id, model_id, req.version_id, approved_by=actor.actor_id)


@router.post("/models/{model_id}/rollback", response_model=ModelDefinition)
async def rollback_model(
    model_id: str,
    req: RollbackModelRequest,
    actor: Actor = Depends(get_current_actor),
) -> ModelDefinition:
    reg = ModelRegistryService.get_instance()
    return await reg.rollback_service.rollback_model(
        actor.organization_id, model_id, reason=req.reason, operator_id=actor.actor_id
    )
