"""Machine-readable experiment result persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def write_experiment_report(
    metrics: dict[str, Any], predictions: pd.DataFrame, output_dir: Path
) -> None:
    """Persist metrics and row-level predictions for auditability."""

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8"
    )
    predictions.to_csv(output_dir / "predictions.csv", index=False)
