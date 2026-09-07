"""
ML Platform CLI — Typer commands for inspecting models, predictions, drift, canary, and rollback.
"""

from __future__ import annotations

import asyncio

import typer

from backend.ml.domain.models import PredictionRequest
from backend.ml.inference.prediction_service import PredictionService
from backend.ml.lineage.lineage_service import DecisionLineageService
from backend.ml.registry.model_registry import ModelRegistryService

ml_app = typer.Typer(name="ml", help="Predictive ML Platform commands")


@ml_app.command("models")
def list_models_cmd(org_id: str = typer.Option(..., "--org-id", "-o", help="Organization ID")) -> None:
    """List all registered ML models."""
    reg = ModelRegistryService.get_instance()
    models = asyncio.run(reg.list_models(org_id))
    typer.echo(f"=== Registered ML Models ({len(models)}) ===")
    for m in models:
        typer.echo(
            f"[{m.model_id}] {m.name} ({m.model_type.value}) - Stage: {m.stage.value} | Active Ver: {m.active_version_id or 'None'}"
        )


@ml_app.command("predict")
def predict_cmd(
    model_id: str = typer.Argument(..., help="Model ID to invoke"),
    org_id: str = typer.Option(..., "--org-id", "-o", help="Organization ID"),
    tenure: float = typer.Option(24.0, "--tenure", help="Tenure in months"),
    leaves: float = typer.Option(4.0, "--leaves", help="Leaves in past 90 days"),
    attendance: float = typer.Option(0.95, "--attendance", help="Attendance rate 30d"),
) -> None:
    """Execute governed inference on an active model."""
    svc = PredictionService.get_instance()
    req = PredictionRequest(
        organization_id=org_id,
        model_id=model_id,
        actor_id="cli-user",
        actor_roles=["HR_MANAGER"],
        input_features={
            "employee_tenure_months": tenure,
            "leave_frequency_90d": leaves,
            "attendance_rate_30d": attendance,
        },
    )
    res = asyncio.run(svc.predict(req))
    typer.echo("=== Prediction Result ===")
    typer.echo(f"Decision: {res.decision.value}")
    typer.echo(f"Probability: {res.probability} | Confidence: {res.confidence:.3f}")
    if res.abstain_reason:
        typer.echo(f"Abstain Reason: {res.abstain_reason}")
    typer.echo(f"Lineage ID: {res.lineage_id}")


@ml_app.command("lineage")
def show_lineage_cmd(
    org_id: str = typer.Option(..., "--org-id", "-o", help="Organization ID"),
    model_id: str = typer.Option(..., "--model-id", "-m", help="Model ID"),
) -> None:
    """Show recent decision lineage records for a model."""
    lin_svc = DecisionLineageService.get_instance()
    records = asyncio.run(lin_svc.list_model_lineages(org_id, model_id, limit=10))
    typer.echo(f"=== Decision Lineage for [{model_id}] ({len(records)} records) ===")
    for r in records:
        typer.echo(
            f"[{r.lineage_id}] Pred: {r.prediction_id} | Ver: v{r.model_version} | Decision: {r.decision.value} | Conf: {r.confidence:.2f}"
        )


@ml_app.command("rollback")
def rollback_cmd(
    model_id: str = typer.Argument(..., help="Model ID to rollback"),
    org_id: str = typer.Option(..., "--org-id", "-o", help="Organization ID"),
    reason: str = typer.Option("Manual operational rollback", "--reason", "-r", help="Rollback reason"),
) -> None:
    """Rollback model to previous stable target version."""
    reg = ModelRegistryService.get_instance()
    m = asyncio.run(reg.rollback_service.rollback_model(org_id, model_id, reason=reason, operator_id="cli-admin"))
    typer.echo(f"Successfully rolled back model [{model_id}]. Active version is now [{m.active_version_id}].")
