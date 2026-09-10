"""Numerically robust helpers shared by feature extractors."""

from __future__ import annotations

import numpy as np


def finite_xy(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return sorted finite x/y pairs with duplicate x coordinates averaged."""

    mask = np.isfinite(x) & np.isfinite(y)
    x_clean = np.asarray(x[mask], dtype=float)
    y_clean = np.asarray(y[mask], dtype=float)
    if x_clean.size == 0:
        return x_clean, y_clean
    order = np.argsort(x_clean, kind="stable")
    x_clean, y_clean = x_clean[order], y_clean[order]
    unique, inverse = np.unique(x_clean, return_inverse=True)
    if unique.size != x_clean.size:
        totals = np.bincount(inverse, weights=y_clean)
        counts = np.bincount(inverse)
        y_clean = totals / counts
        x_clean = unique
    return x_clean, y_clean


def interpolate_if_supported(x: np.ndarray, y: np.ndarray, point: float) -> float:
    """Interpolate only inside observed support; never extrapolate silently."""

    x_clean, y_clean = finite_xy(x, y)
    if x_clean.size < 2:
        return float("nan")
    if point < x_clean[0]:
        if not np.isclose(point, x_clean[0]):
            return float("nan")
        point = float(x_clean[0])
    if point > x_clean[-1]:
        if not np.isclose(point, x_clean[-1]):
            return float("nan")
        point = float(x_clean[-1])
    return float(np.interp(point, x_clean, y_clean))


def linear_slope(x: np.ndarray, y: np.ndarray) -> float:
    """Return least-squares slope, or NaN when the design is degenerate."""

    x_clean, y_clean = finite_xy(x, y)
    if x_clean.size < 2 or np.ptp(x_clean) == 0:
        return float("nan")
    return float(np.polyfit(x_clean, y_clean, deg=1)[0])
