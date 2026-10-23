"""
Feature Validation Engine — Validates schema, types, range bounds, null rates, and distribution boundaries.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any, NamedTuple

from backend.ml.domain.enums import FeatureDataType
from backend.ml.domain.models import FeatureDefinition

logger = logging.getLogger(__name__)


class FeatureValidationResult(NamedTuple):
    is_valid: bool
    errors: list[str]
    out_of_distribution: bool
    missing_required_features: list[str]


class FeatureValidator:
    """Validates runtime feature vectors against registered FeatureDefinitions."""

    @staticmethod
    def validate_vector(
        features: dict[str, Any],
        definitions: Sequence[FeatureDefinition],
        allow_missing: bool = False,
    ) -> FeatureValidationResult:
        """
        Validate feature values against definitions:
        1. Required feature presence.
        2. Type correctness.
        3. Min/Max range constraints.
        4. Categorical membership constraints.
        """
        errors: list[str] = []
        missing: list[str] = []
        ood = False

        def_map = {d.name: d for d in definitions}

        # 1. Check required features
        for d in definitions:
            if d.name not in features or features[d.name] is None:
                missing.append(d.name)
                if not allow_missing:
                    errors.append(f"Missing required feature: '{d.name}'")

        # 2. Check types and bounds for provided features
        for f_name, f_val in features.items():
            if f_val is None:
                continue

            f_def = def_map.get(f_name)
            if not f_def:
                continue  # Ignore undeclared extra features

            # Validate numeric bounds
            if f_def.datatype == FeatureDataType.NUMERIC:
                if not isinstance(f_val, (int, float)):
                    errors.append(f"Feature '{f_name}' expected NUMERIC, got {type(f_val).__name__}")
                    continue

                if f_def.min_value is not None and f_val < f_def.min_value:
                    errors.append(f"Feature '{f_name}' value {f_val} < min_value {f_def.min_value}")
                    ood = True
                if f_def.max_value is not None and f_val > f_def.max_value:
                    errors.append(f"Feature '{f_name}' value {f_val} > max_value {f_def.max_value}")
                    ood = True

            # Validate categorical bounds
            elif f_def.datatype == FeatureDataType.CATEGORICAL:
                if f_def.allowed_categories and str(f_val) not in f_def.allowed_categories:
                    errors.append(f"Feature '{f_name}' value '{f_val}' not in allowed categories {f_def.allowed_categories}")
                    ood = True

        is_valid = len(errors) == 0
        return FeatureValidationResult(
            is_valid=is_valid,
            errors=errors,
            out_of_distribution=ood,
            missing_required_features=missing,
        )
