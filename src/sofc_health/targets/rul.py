"""Threshold-based RUL labels with explicit censoring."""

from __future__ import annotations

import numpy as np
import pandas as pd


def add_rul_target(
    frame: pd.DataFrame,
    *,
    soh_column: str = "soh_composite_pct",
    threshold_pct: float = 80.0,
    consecutive_below: int = 3,
) -> pd.DataFrame:
    """Add sustained-threshold RUL and a right-censoring indicator.

    The output is deliberately named ``rul_assessments`` rather than hours: the source
    dataset does not provide a field-operating-hours clock.
    """

    if not 0 < threshold_pct < 100:
        raise ValueError("threshold_pct must lie strictly between 0 and 100")
    if consecutive_below < 1:
        raise ValueError("consecutive_below must be positive")
    if soh_column not in frame:
        raise ValueError(f"Missing SOH column: {soh_column}")

    result = frame.sort_values(["cell_id", "assessment_index"]).copy()
    result["eol_assessment"] = np.nan
    result["rul_assessments"] = np.nan
    result["rul_right_censored"] = True
    for _, indices in result.groupby("cell_id", sort=False).groups.items():
        cell = result.loc[indices]
        below = (cell[soh_column] <= threshold_pct).fillna(False).to_numpy(dtype=int)
        if below.size < consecutive_below:
            continue
        sustained = np.convolve(below, np.ones(consecutive_below, dtype=int), mode="valid")
        starts = np.flatnonzero(sustained == consecutive_below)
        if starts.size == 0:
            continue
        eol = int(cell["assessment_index"].iloc[int(starts[0])])
        result.loc[indices, "eol_assessment"] = eol
        result.loc[indices, "rul_assessments"] = (
            eol - result.loc[indices, "assessment_index"]
        ).clip(lower=0)
        result.loc[indices, "rul_right_censored"] = False
    return result
