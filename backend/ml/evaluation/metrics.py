"""
Evaluation Metrics — Statistical algorithms for Classification, Regression, Ranking, Forecasting, and Anomaly models.
"""

from __future__ import annotations

import math
from collections.abc import Sequence


class ModelMetricsCalculator:
    """Computes standard evaluation metrics without requiring external C-extensions."""

    @staticmethod
    def classification_metrics(
        y_true: Sequence[int],
        y_pred: Sequence[int],
        y_prob: Sequence[float] | None = None,
    ) -> dict[str, float]:
        """Compute Accuracy, Precision, Recall, F1, and approximate ROC-AUC."""
        if not y_true or len(y_true) != len(y_pred):
            return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0}

        tp = sum(1 for yt, yp in zip(y_true, y_pred, strict=False) if yt == 1 and yp == 1)
        fp = sum(1 for yt, yp in zip(y_true, y_pred, strict=False) if yt == 0 and yp == 1)
        fn = sum(1 for yt, yp in zip(y_true, y_pred, strict=False) if yt == 1 and yp == 0)
        tn = sum(1 for yt, yp in zip(y_true, y_pred, strict=False) if yt == 0 and yp == 0)

        n = len(y_true)
        accuracy = round((tp + tn) / n, 4)
        precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
        recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
        f1 = round(2 * (precision * recall) / (precision + recall), 4) if (precision + recall) > 0 else 0.0

        metrics: dict[str, float] = {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "tp": float(tp),
            "fp": float(fp),
            "fn": float(fn),
            "tn": float(tn),
        }

        # Approximate ROC-AUC via rank-order concordance if probabilities are provided
        if y_prob and len(y_prob) == len(y_true):
            pairs = list(zip(y_true, y_prob, strict=False))
            positives = [p for yt, p in pairs if yt == 1]
            negatives = [p for yt, p in pairs if yt == 0]
            if positives and negatives:
                concordant = sum(1 for pos in positives for neg in negatives if pos > neg)
                ties = sum(0.5 for pos in positives for neg in negatives if pos == neg)
                auc = round((concordant + ties) / (len(positives) * len(negatives)), 4)
                metrics["roc_auc"] = auc

        return metrics

    @staticmethod
    def regression_metrics(
        y_true: Sequence[float],
        y_pred: Sequence[float],
    ) -> dict[str, float]:
        """Compute MAE, RMSE, and R²."""
        if not y_true or len(y_true) != len(y_pred):
            return {"mae": 0.0, "rmse": 0.0, "r2": 0.0}

        n = len(y_true)
        errors = [yt - yp for yt, yp in zip(y_true, y_pred, strict=False)]
        mae = round(sum(abs(e) for e in errors) / n, 4)
        mse = sum(e**2 for e in errors) / n
        rmse = round(math.sqrt(mse), 4)

        mean_true = sum(y_true) / n
        ss_tot = sum((yt - mean_true) ** 2 for yt in y_true)
        ss_res = sum(e**2 for e in errors)
        r2 = round(1.0 - (ss_res / ss_tot), 4) if ss_tot > 0 else 0.0

        return {"mae": mae, "rmse": rmse, "r2": r2}

    @staticmethod
    def ranking_metrics(
        actual_relevant: Sequence[Sequence[str]],
        ranked_predictions: Sequence[Sequence[str]],
        k: int = 5,
    ) -> dict[str, float]:
        """Compute Precision@K, Recall@K, and Mean Reciprocal Rank (MRR)."""
        if not actual_relevant or len(actual_relevant) != len(ranked_predictions):
            return {"precision_at_k": 0.0, "recall_at_k": 0.0, "mrr": 0.0}

        precisions: list[float] = []
        recalls: list[float] = []
        reciprocal_ranks: list[float] = []

        for actual, ranked in zip(actual_relevant, ranked_predictions, strict=False):
            top_k = ranked[:k]
            actual_set = set(actual)
            if not actual_set:
                continue

            hits = sum(1 for item in top_k if item in actual_set)
            precisions.append(hits / max(1, len(top_k)))
            recalls.append(hits / len(actual_set))

            rr = 0.0
            for rank_idx, item in enumerate(ranked):
                if item in actual_set:
                    rr = 1.0 / (rank_idx + 1)
                    break
            reciprocal_ranks.append(rr)

        num_queries = max(1, len(precisions))
        return {
            f"precision_at_{k}": round(sum(precisions) / num_queries, 4),
            f"recall_at_{k}": round(sum(recalls) / num_queries, 4),
            "mrr": round(sum(reciprocal_ranks) / max(1, len(reciprocal_ranks)), 4),
        }

    @staticmethod
    def anomaly_metrics(
        y_true: Sequence[int],
        anomaly_scores: Sequence[float],
        threshold: float = 0.70,
    ) -> dict[str, float]:
        """Compute Anomaly Precision, Recall, and False Positive Rate."""
        y_pred = [1 if s >= threshold else 0 for s in anomaly_scores]
        class_res = ModelMetricsCalculator.classification_metrics(y_true, y_pred)
        tn = class_res.get("tn", 0.0)
        fp = class_res.get("fp", 0.0)
        fpr = round(fp / (fp + tn), 4) if (fp + tn) > 0 else 0.0
        return {
            "precision": class_res["precision"],
            "recall": class_res["recall"],
            "f1": class_res["f1"],
            "false_positive_rate": fpr,
        }
