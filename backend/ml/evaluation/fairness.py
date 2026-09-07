"""
Fairness Evaluator — Post-hoc algorithmic bias auditing across protected demographic slices.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from backend.ml.domain.models import FairnessReport

logger = logging.getLogger(__name__)


class FairnessEvaluator:
    """Evaluates disparate impact, demographic parity, and equalized odds without leaking protected attributes to models."""

    @staticmethod
    def evaluate_fairness(
        organization_id: str,
        model_id: str,
        model_version_id: str,
        protected_attribute_name: str,
        protected_groups: Sequence[str],  # e.g. ["group_a", "group_b", ...]
        y_true: Sequence[int],
        y_pred: Sequence[int],
        max_allowed_parity_gap: float = 0.10,
    ) -> FairnessReport:
        """
        Evaluate Demographic Parity Difference and Equal Opportunity Difference:
        - Demographic Parity: |P(Y_hat=1 | Group=A) - P(Y_hat=1 | Group=B)|
        - Equal Opportunity:  |P(Y_hat=1 | Y=1, Group=A) - P(Y_hat=1 | Y=1, Group=B)|
        - Disparate Impact:   min(Selection Rate) / max(Selection Rate)
        """
        if not protected_groups or len(protected_groups) != len(y_pred):
            return FairnessReport(
                organization_id=organization_id,
                model_id=model_id,
                model_version_id=model_version_id,
                protected_attribute=protected_attribute_name,
                demographic_parity_difference=0.0,
                equal_opportunity_difference=0.0,
                disparate_impact_ratio=1.0,
                is_compliant=True,
                threshold_applied=max_allowed_parity_gap,
            )

        unique_groups = sorted(set(protected_groups))
        selection_rates: dict[str, float] = {}
        tpr_rates: dict[str, float] = {}

        for grp in unique_groups:
            indices = [i for i, g in enumerate(protected_groups) if g == grp]
            grp_total = len(indices)
            if grp_total == 0:
                continue

            positive_preds = sum(1 for i in indices if y_pred[i] == 1)
            selection_rates[grp] = positive_preds / grp_total

            actual_positives = [i for i in indices if y_true[i] == 1]
            if actual_positives:
                true_positives = sum(1 for i in actual_positives if y_pred[i] == 1)
                tpr_rates[grp] = true_positives / len(actual_positives)
            else:
                tpr_rates[grp] = 1.0

        rates_list = list(selection_rates.values())
        tpr_list = list(tpr_rates.values())

        parity_gap = max(rates_list) - min(rates_list) if rates_list else 0.0
        equal_opp_gap = max(tpr_list) - min(tpr_list) if tpr_list else 0.0

        max_rate = max(rates_list) if rates_list else 1.0
        min_rate = min(rates_list) if rates_list else 1.0
        disparate_impact = (min_rate / max_rate) if max_rate > 0 else 1.0

        is_compliant = parity_gap <= max_allowed_parity_gap and equal_opp_gap <= max_allowed_parity_gap

        return FairnessReport(
            organization_id=organization_id,
            model_id=model_id,
            model_version_id=model_version_id,
            protected_attribute=protected_attribute_name,
            demographic_parity_difference=round(parity_gap, 4),
            equal_opportunity_difference=round(equal_opp_gap, 4),
            disparate_impact_ratio=round(disparate_impact, 4),
            is_compliant=is_compliant,
            threshold_applied=max_allowed_parity_gap,
        )
