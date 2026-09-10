"""Run reproducible rolling-origin SOH baselines from the repository root."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sofc_health.evaluation.backtest import rolling_backtest
from sofc_health.evaluation.report import write_experiment_report
from sofc_health.models.baselines import drift, persistence
from sofc_health.models.statistical import exponential_smoothing_forecast
from sofc_health.validation.metrics import regression_metrics


def main() -> None:
    modeling_path = Path("data/processed/modeling_table.parquet")
    if not modeling_path.exists():
        raise FileNotFoundError("Run `sofc-health all` before baseline experiments.")
    frame = pd.read_parquet(modeling_path)
    models = {
        "persistence": persistence,
        "drift": drift,
        "exponential_smoothing": exponential_smoothing_forecast,
    }
    predictions: list[pd.DataFrame] = []
    metrics: dict[str, dict[str, float]] = {}
    for name, function in models.items():
        result = rolling_backtest(
            frame,
            function,
            target="soh_composite_pct",
            min_history=8,
            horizon=1,
        )
        result.insert(0, "model", name)
        predictions.append(result)
        metrics[name] = regression_metrics(result["y_true"].to_numpy(), result["y_pred"].to_numpy())
    all_predictions = pd.concat(predictions, ignore_index=True)
    write_experiment_report(metrics, all_predictions, Path("reports/tables/baselines"))
    for model, values in metrics.items():
        print(model, {key: round(value, 4) for key, value in values.items()})


if __name__ == "__main__":
    main()
