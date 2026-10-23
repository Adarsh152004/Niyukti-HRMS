"""
Tests for ML Domain Models, Enums, ModelCards, and Events.
"""

from __future__ import annotations

from backend.ml.domain.enums import (
    FeatureDataType,
    FeatureSensitivity,
    ModelStage,
    ModelType,
)
from backend.ml.domain.events import MLModelRegistered
from backend.ml.domain.models import (
    FeatureDefinition,
    ModelCard,
    ModelDefinition,
)


def test_model_definition_and_card():
    card = ModelCard(
        purpose="Forecast employee attrition risk over 90-day horizon",
        intended_users=["HR Business Partners", "People Managers"],
        prohibited_uses=["Automated employee termination"],
        target_demographics="Full-time and contract employees",
        training_data_summary="200 synthetic records with temporal split",
        features_used=["employee_tenure_months", "leave_frequency_90d"],
        ethical_considerations=["Must not be used for direct adverse employment actions."],
        known_limitations=["Baseline model calibrated on synthetic benchmark data."],
        evaluation_summary={"accuracy": 0.88, "f1": 0.85},
        human_in_the_loop_requirements="High risk cases (>0.80) require manager 1-on-1 before intervention.",
    )

    model = ModelDefinition(
        organization_id="org-test-ml",
        name="AttritionRiskPredictor",
        model_type=ModelType.CLASSIFICATION,
        stage=ModelStage.DEVELOPMENT,
    )

    assert model.model_id.startswith("mdl-")
    assert model.stage == ModelStage.DEVELOPMENT
    assert card.purpose.startswith("Forecast")
    assert "Automated employee termination" in card.prohibited_uses


def test_feature_definition_and_events():
    feat = FeatureDefinition(
        name="engagement_score",
        datatype=FeatureDataType.NUMERIC,
        source_table="surveys",
        transformation_logic="normalized_survey_index",
        sensitivity=FeatureSensitivity.INTERNAL,
        owner="people-ops",
        min_value=0.0,
        max_value=100.0,
    )
    assert feat.name == "engagement_score"
    assert feat.min_value == 0.0

    ev = MLModelRegistered(organization_id="org-1", model_id="mdl-101", model_name="TestModel")
    assert ev.event_type == "ml.model.registered"
    assert ev.payload["model_name"] == "TestModel"
