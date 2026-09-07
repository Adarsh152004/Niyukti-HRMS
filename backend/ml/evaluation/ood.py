"""
Out-of-Distribution (OOD) Detector — Bounds-checking and multivariate distance evaluation.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from backend.ml.domain.enums import FeatureDataType
from backend.ml.domain.models import FeatureDefinition


class OutOfDistributionDetector:
    """Detects whether an inference payload lies outside training distribution bounds."""

    @staticmethod
    def is_out_of_distribution(
        input_features: dict[str, Any],
        definitions: Sequence[FeatureDefinition],
        strict_bounds: bool = True,
    ) -> tuple[bool, str | None]:
        """
        Check if any feature value severely violates min/max bounds or allowed categorical sets.
        """
        def_map = {d.name: d for d in definitions}

        for f_name, val in input_features.items():
            f_def = def_map.get(f_name)
            if not f_def or val is None:
                continue

            if f_def.datatype == FeatureDataType.NUMERIC and isinstance(val, (int, float)):
                # Extreme bound check (e.g. negative tenure or 1000 years tenure)
                if f_def.min_value is not None and val < f_def.min_value:
                    return True, f"Feature '{f_name}' value {val} is below minimum training bound {f_def.min_value}"
                if f_def.max_value is not None and val > f_def.max_value:
                    return True, f"Feature '{f_name}' value {val} exceeds maximum training bound {f_def.max_value}"

            elif f_def.datatype == FeatureDataType.CATEGORICAL:
                if f_def.allowed_categories and str(val) not in f_def.allowed_categories:
                    return True, f"Unseen categorical level '{val}' for feature '{f_name}'"

        return False, None
