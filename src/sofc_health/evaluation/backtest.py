"""Rolling-origin evaluation for univariate degradation trajectories."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd

ForecastFunction = Callable[[np.ndarray, int], np.ndarray]


def rolling_backtest(
    frame: pd.DataFrame,
    forecast: ForecastFunction,
    *,
    target: str,
    min_history: int = 8,
    horizon: int = 1,
) -> pd.DataFrame:
    """Backtest a forecast function independently on each cell."""

    rows: list[dict[str, float | int | str]] = []
    for cell_id, group in frame.groupby("cell_id", sort=True):
        cell = group.sort_values("assessment_index").dropna(subset=[target])
        values = cell[target].to_numpy(dtype=float)
        assessments = cell["assessment_index"].to_numpy(dtype=int)
        for origin in range(min_history, len(cell) - horizon + 1):
            prediction = forecast(values[:origin], horizon)
            for offset in range(horizon):
                rows.append(
                    {
                        "cell_id": str(cell_id),
                        "origin_assessment": int(assessments[origin - 1]),
                        "target_assessment": int(assessments[origin + offset]),
                        "horizon": offset + 1,
                        "y_true": float(values[origin + offset]),
                        "y_pred": float(prediction[offset]),
                    }
                )
    return pd.DataFrame(rows)
