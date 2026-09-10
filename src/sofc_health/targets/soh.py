"""Transparent SOH candidates derived from measured SOFC performance."""

from __future__ import annotations

import numpy as np
import pandas as pd

PERFORMANCE_COLUMNS = {
    "current": "tr_performance_current_a_cm2",
    "power": "iv_max_power_w_cm2",
    "iv_0p70v": "iv_current_at_0p70v_a_cm2",
}


def _normalize_to_cell_baseline(series: pd.Series) -> pd.Series:
    valid = series.dropna()
    if valid.empty or valid.iloc[0] <= 0:
        return pd.Series(np.nan, index=series.index, dtype=float)
    return 100.0 * series / float(valid.iloc[0])


def add_soh_targets(features: pd.DataFrame) -> pd.DataFrame:
    """Add single-signal and composite SOH candidates.

    SOH is normalized within each cell because cells have different initial performance.
    The composite is a geometric mean so one weak modality cannot be hidden by a large
    arithmetic compensation in another. Values are not forced to be monotonic.
    """

    required = {"cell_id", "assessment_index", *PERFORMANCE_COLUMNS.values()}
    missing = sorted(required - set(features.columns))
    if missing:
        raise ValueError(f"Feature table missing SOH inputs: {missing}")

    result = features.sort_values(["cell_id", "assessment_index"]).copy()
    target_columns: list[str] = []
    for label, performance_column in PERFORMANCE_COLUMNS.items():
        target = f"soh_{label}_pct"
        result[target] = result.groupby("cell_id", sort=False)[performance_column].transform(
            _normalize_to_cell_baseline
        )
        target_columns.append(target)

    positive = result[target_columns].clip(lower=1.0e-6)
    available = positive.notna().sum(axis=1)
    result["soh_composite_pct"] = np.exp(np.log(positive).sum(axis=1) / available).where(
        available >= 2
    )
    return result
