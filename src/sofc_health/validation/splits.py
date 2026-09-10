"""Cross-cell and chronological validation strategies."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Fold:
    """Indices and semantic identity of one validation fold."""

    name: str
    train_indices: np.ndarray
    test_indices: np.ndarray


def leave_one_cell_out(frame: pd.DataFrame) -> Iterator[Fold]:
    """Yield domain-generalization folds with a completely unseen test cell."""

    if "cell_id" not in frame:
        raise ValueError("frame must contain cell_id")
    for cell_id in sorted(frame["cell_id"].unique()):
        test = frame.index[frame["cell_id"] == cell_id].to_numpy()
        train = frame.index[frame["cell_id"] != cell_id].to_numpy()
        if train.size and test.size:
            yield Fold(f"holdout_{cell_id}", train, test)


def rolling_origin_splits(
    frame: pd.DataFrame,
    *,
    cell_id: str,
    min_train_assessments: int,
    horizon: int = 1,
    step: int = 1,
    gap: int = 0,
) -> Iterator[Fold]:
    """Yield expanding-window folds for one cell while preserving chronology."""

    if min_train_assessments < 2 or horizon < 1 or step < 1 or gap < 0:
        raise ValueError("Invalid rolling-origin parameters")
    cell = frame.loc[frame["cell_id"] == cell_id].sort_values("assessment_index")
    assessments = cell["assessment_index"].drop_duplicates().to_numpy()
    stop = len(assessments) - gap - horizon + 1
    for train_size in range(min_train_assessments, stop, step):
        train_assessments = assessments[:train_size]
        test_start = train_size + gap
        test_assessments = assessments[test_start : test_start + horizon]
        train = cell.index[cell["assessment_index"].isin(train_assessments)].to_numpy()
        test = cell.index[cell["assessment_index"].isin(test_assessments)].to_numpy()
        if test.size:
            yield Fold(f"{cell_id}_origin_{int(train_assessments[-1])}_h{horizon}", train, test)
