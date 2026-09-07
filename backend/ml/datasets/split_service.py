"""
Dataset Splitting Service — Deterministic dataset partitioning preventing data leakage.
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from typing import Any, NamedTuple


class DatasetSplitResult(NamedTuple):
    train_data: list[dict[str, Any]]
    val_data: list[dict[str, Any]]
    test_data: list[dict[str, Any]]


class DatasetSplitService:
    """Partitions datasets into train/validation/test sets deterministically."""

    @staticmethod
    def random_split(
        rows: Sequence[dict[str, Any]],
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        seed: int = 42,
    ) -> DatasetSplitResult:
        """Deterministic random split using fixed seed."""
        if not rows:
            return DatasetSplitResult([], [], [])

        shuffled = list(rows)
        rng = random.Random(seed)
        rng.shuffle(shuffled)

        n = len(shuffled)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)

        train = shuffled[:n_train]
        val = shuffled[n_train : n_train + n_val]
        test = shuffled[n_train + n_val :]

        return DatasetSplitResult(train_data=train, val_data=val, test_data=test)

    @staticmethod
    def temporal_split(
        rows: Sequence[dict[str, Any]],
        timestamp_field: str = "record_date",
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
    ) -> DatasetSplitResult:
        """Time-ordered dataset split ensuring no future leakage into training sets."""
        if not rows:
            return DatasetSplitResult([], [], [])

        sorted_rows = sorted(rows, key=lambda r: str(r.get(timestamp_field, "")))
        n = len(sorted_rows)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)

        train = sorted_rows[:n_train]
        val = sorted_rows[n_train : n_train + n_val]
        test = sorted_rows[n_train + n_val :]

        return DatasetSplitResult(train_data=train, val_data=val, test_data=test)

    @staticmethod
    def entity_grouped_split(
        rows: Sequence[dict[str, Any]],
        group_field: str = "employee_id",
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        seed: int = 42,
    ) -> DatasetSplitResult:
        """Grouped split ensuring all records of a specific entity (e.g. employee) reside in one partition only."""
        if not rows:
            return DatasetSplitResult([], [], [])

        groups: dict[str, list[dict[str, Any]]] = {}
        for r in rows:
            g_val = str(r.get(group_field, "unknown"))
            if g_val not in groups:
                groups[g_val] = []
            groups[g_val].append(r)

        unique_groups = list(groups.keys())
        rng = random.Random(seed)
        rng.shuffle(unique_groups)

        n_g = len(unique_groups)
        n_train = int(n_g * train_ratio)
        n_val = int(n_g * val_ratio)

        train_groups = set(unique_groups[:n_train])
        val_groups = set(unique_groups[n_train : n_train + n_val])

        train_rows: list[dict[str, Any]] = []
        val_rows: list[dict[str, Any]] = []
        test_rows: list[dict[str, Any]] = []

        for g_val, r_list in groups.items():
            if g_val in train_groups:
                train_rows.extend(r_list)
            elif g_val in val_groups:
                val_rows.extend(r_list)
            else:
                test_rows.extend(r_list)

        return DatasetSplitResult(train_data=train_rows, val_data=val_rows, test_data=test_rows)
