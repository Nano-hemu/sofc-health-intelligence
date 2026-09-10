"""Tabular supervised-learning utilities for assessment-level forecasting."""

from __future__ import annotations

from typing import Literal

import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

ModelName = Literal["ridge", "extra_trees", "hist_gradient_boosting"]


def add_lag_features(
    frame: pd.DataFrame,
    columns: list[str],
    *,
    lags: tuple[int, ...] = (1, 2, 3),
) -> pd.DataFrame:
    """Create causal lags within each cell; the current target is never used as a feature."""

    result = frame.sort_values(["cell_id", "assessment_index"]).copy()
    grouped = result.groupby("cell_id", sort=False)
    generated: dict[str, pd.Series] = {}
    for column in columns:
        for lag in lags:
            generated[f"{column}_lag{lag}"] = grouped[column].shift(lag)
        generated[f"{column}_delta1"] = grouped[column].diff(1)
    return pd.concat([result, pd.DataFrame(generated, index=result.index)], axis=1)


def make_regressor(name: ModelName, *, random_state: int = 42) -> object:
    """Return a deterministic, industry-standard regression baseline."""

    if name == "ridge":
        return Pipeline([("scale", RobustScaler()), ("model", Ridge(alpha=1.0))])
    if name == "extra_trees":
        return ExtraTreesRegressor(
            n_estimators=500,
            min_samples_leaf=2,
            max_features=0.8,
            random_state=random_state,
            n_jobs=-1,
        )
    if name == "hist_gradient_boosting":
        return HistGradientBoostingRegressor(
            learning_rate=0.05,
            max_iter=300,
            max_leaf_nodes=15,
            l2_regularization=1.0,
            random_state=random_state,
        )
    raise ValueError(f"Unknown model: {name}")
