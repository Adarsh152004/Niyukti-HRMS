"""
ML Deployment Gate — Enforces multi-criteria compliance gates before model activation.
"""

from __future__ import annotations

import logging
from typing import NamedTuple

from backend.ml.domain.models import ModelVersion

logger = logging.getLogger(__name__)


class DeploymentGateResult(NamedTuple):
    is_approved: bool
    rejection_reasons: list[str]
    performance_passed: bool
    fairness_passed: bool
    calibration_passed: bool


class MLDeploymentGate:
    """Evaluates whether a ModelVersion candidate satisfies governance deployment criteria."""

    @staticmethod
    def evaluate_gate(
        version: ModelVersion,
        min_accuracy: float = 0.65,
        max_ece: float = 0.25,
        max_fairness_gap: float = 0.15,
    ) -> DeploymentGateResult:
        """
        Evaluate:
        1. Performance threshold (Accuracy >= min_accuracy).
        2. Calibration threshold (ECE <= max_ece).
        3. Algorithmic fairness threshold (Demographic parity gap <= max_fairness_gap).
        """
        reasons: list[str] = []

        # 1. Performance Check
        acc = version.metrics.get("accuracy", 1.0)
        perf_passed = acc >= min_accuracy
        if not perf_passed:
            reasons.append(f"Model accuracy {acc:.3f} < minimum required {min_accuracy:.3f}")

        # 2. Calibration Check
        ece = version.calibration_metrics.get("expected_calibration_error", 0.0)
        calib_passed = ece <= max_ece
        if not calib_passed:
            reasons.append(f"Expected calibration error {ece:.3f} > maximum allowed {max_ece:.3f}")

        # 3. Fairness Check
        fair_gap = version.fairness_metrics.get("demographic_parity_difference", 0.0)
        fairness_passed = fair_gap <= max_fairness_gap
        if not fairness_passed:
            reasons.append(f"Fairness parity gap {fair_gap:.3f} > maximum allowed {max_fairness_gap:.3f}")

        approved = perf_passed and calib_passed and fairness_passed

        return DeploymentGateResult(
            is_approved=approved,
            rejection_reasons=reasons,
            performance_passed=perf_passed,
            fairness_passed=fairness_passed,
            calibration_passed=calib_passed,
        )
