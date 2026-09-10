"""Forecast and uncertainty metrics with explicit failure behavior."""

from __future__ import annotations

import numpy as np


def regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    naive_scale: float | None = None,
) -> dict[str, float]:
    """Compute error magnitude, bias, fit, and optionally MASE."""

    actual = np.asarray(y_true, dtype=float)
    predicted = np.asarray(y_pred, dtype=float)
    mask = np.isfinite(actual) & np.isfinite(predicted)
    actual, predicted = actual[mask], predicted[mask]
    if actual.size == 0:
        raise ValueError("No finite prediction pairs")
    error = predicted - actual
    denominator = np.sum((actual - actual.mean()) ** 2)
    metrics = {
        "mae": float(np.mean(np.abs(error))),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "bias": float(np.mean(error)),
        "r2": float(1.0 - np.sum(error**2) / denominator) if denominator > 0 else float("nan"),
    }
    if naive_scale is not None:
        metrics["mase"] = float(metrics["mae"] / naive_scale) if naive_scale > 0 else float("nan")
    return metrics


def interval_metrics(y_true: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> dict[str, float]:
    """Return empirical coverage and mean prediction-interval width."""

    actual = np.asarray(y_true, dtype=float)
    low = np.asarray(lower, dtype=float)
    high = np.asarray(upper, dtype=float)
    mask = np.isfinite(actual) & np.isfinite(low) & np.isfinite(high)
    if not mask.any():
        raise ValueError("No finite interval rows")
    if np.any(low[mask] > high[mask]):
        raise ValueError("Lower interval bound exceeds upper bound")
    covered = (actual[mask] >= low[mask]) & (actual[mask] <= high[mask])
    return {
        "coverage": float(np.mean(covered)),
        "mean_interval_width": float(np.mean(high[mask] - low[mask])),
    }
