"""Mandatory forecasting baselines for honest model comparison."""

from __future__ import annotations

import numpy as np


def persistence(history: np.ndarray, horizon: int) -> np.ndarray:
    """Forecast the most recent observation at every future horizon."""

    values = np.asarray(history, dtype=float)
    if values.size == 0 or horizon < 1:
        raise ValueError("Persistence needs history and a positive horizon")
    return np.asarray(np.repeat(values[-1], horizon), dtype=float)


def drift(history: np.ndarray, horizon: int) -> np.ndarray:
    """Extrapolate the average historical change from first to last observation."""

    values = np.asarray(history, dtype=float)
    if values.size < 2 or horizon < 1:
        raise ValueError("Drift needs two observations and a positive horizon")
    slope = (values[-1] - values[0]) / (values.size - 1)
    return np.asarray(values[-1] + slope * np.arange(1, horizon + 1), dtype=float)


def damped_local_trend(history: np.ndarray, horizon: int, damping: float = 0.8) -> np.ndarray:
    """Project the latest change with geometrically decreasing influence."""

    values = np.asarray(history, dtype=float)
    if values.size < 2 or horizon < 1 or not 0 <= damping <= 1:
        raise ValueError("Invalid damped-trend inputs")
    last_change = values[-1] - values[-2]
    increments = last_change * damping ** np.arange(1, horizon + 1)
    return np.asarray(values[-1] + np.cumsum(increments), dtype=float)
