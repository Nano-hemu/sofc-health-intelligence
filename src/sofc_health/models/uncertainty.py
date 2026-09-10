"""Distribution-free split-conformal prediction intervals."""

from __future__ import annotations

import numpy as np


def conformal_radius(
    y_calibration: np.ndarray,
    prediction_calibration: np.ndarray,
    *,
    alpha: float = 0.10,
) -> float:
    """Compute the finite-sample corrected absolute-residual quantile."""

    if not 0 < alpha < 1:
        raise ValueError("alpha must lie strictly between 0 and 1")
    residuals = np.abs(
        np.asarray(y_calibration, dtype=float) - np.asarray(prediction_calibration, dtype=float)
    )
    residuals = residuals[np.isfinite(residuals)]
    if residuals.size < 2:
        raise ValueError("At least two finite calibration residuals are required")
    corrected_probability = min(1.0, np.ceil((residuals.size + 1) * (1 - alpha)) / residuals.size)
    return float(np.quantile(residuals, corrected_probability, method="higher"))


def conformal_interval(prediction: np.ndarray, radius: float) -> tuple[np.ndarray, np.ndarray]:
    """Apply a symmetric conformal radius to point predictions."""

    if radius < 0 or not np.isfinite(radius):
        raise ValueError("radius must be finite and non-negative")
    values = np.asarray(prediction, dtype=float)
    return values - radius, values + radius
