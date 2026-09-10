"""Features from constant-voltage current transients."""

from __future__ import annotations

import numpy as np
import pandas as pd

from sofc_health.features.common import finite_xy, linear_slope


def _time_to_fraction(time_s: np.ndarray, current: np.ndarray, fraction: float) -> float:
    initial = float(np.median(current[: max(1, len(current) // 20)]))
    steady = float(np.median(current[-max(3, len(current) // 10) :]))
    target = initial + fraction * (steady - initial)
    if np.isclose(initial, steady):
        return float("nan")
    direction = np.sign(steady - initial)
    reached = np.flatnonzero(direction * (current - target) >= 0)
    return float(time_s[reached[0]]) if reached.size else float("nan")


def extract_transient_features(group: pd.DataFrame) -> dict[str, float]:
    """Summarize one current transient without assuming a global time axis."""

    time_s, current = finite_xy(
        group["elapsed_s"].to_numpy(dtype=float),
        group["current_density_a_cm2"].to_numpy(dtype=float),
    )
    if time_s.size < 5:
        raise ValueError("A transient requires at least five valid time points")

    head_n = max(3, len(current) // 20)
    tail_n = max(5, len(current) // 10)
    initial = float(np.median(current[:head_n]))
    steady = float(np.median(current[-tail_n:]))
    tail_time = time_s[-tail_n:]
    tail_current = current[-tail_n:]
    gap = current - steady

    return {
        "tr_initial_current_a_cm2": initial,
        "tr_steady_current_a_cm2": steady,
        "tr_performance_current_a_cm2": -steady,
        "tr_current_change_a_cm2": steady - initial,
        "tr_t50_s": _time_to_fraction(time_s, current, 0.50),
        "tr_t90_s": _time_to_fraction(time_s, current, 0.90),
        "tr_relaxation_area_a_s_cm2": float(np.trapezoid(np.abs(gap), time_s)),
        "tr_tail_slope_a_cm2_s": linear_slope(tail_time, tail_current),
        "tr_tail_noise_a_cm2": float(np.std(tail_current, ddof=1)),
        "tr_duration_s": float(time_s[-1] - time_s[0]),
        "tr_sample_count": float(time_s.size),
    }
