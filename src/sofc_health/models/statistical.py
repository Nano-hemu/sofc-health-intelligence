"""Statsmodels-based univariate forecasting interfaces."""

from __future__ import annotations

import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX


def exponential_smoothing_forecast(history: np.ndarray, horizon: int) -> np.ndarray:
    """Forecast a level-plus-damped-trend model without invented seasonality."""

    values = np.asarray(history, dtype=float)
    if values.size < 5:
        raise ValueError("Exponential smoothing requires at least five observations")
    fitted = ExponentialSmoothing(
        values, trend="add", damped_trend=True, seasonal=None, initialization_method="estimated"
    ).fit(optimized=True)
    return np.asarray(fitted.forecast(horizon), dtype=float)


def arima_forecast(
    history: np.ndarray, horizon: int, order: tuple[int, int, int] = (1, 1, 0)
) -> np.ndarray:
    """Forecast a compact non-seasonal ARIMA model."""

    values = np.asarray(history, dtype=float)
    if values.size < 8:
        raise ValueError("ARIMA requires at least eight observations")
    fitted = SARIMAX(
        values,
        order=order,
        trend="t" if order[1] > 0 else "c",
        enforce_stationarity=False,
        enforce_invertibility=False,
    ).fit(disp=False)
    return np.asarray(fitted.forecast(horizon), dtype=float)
