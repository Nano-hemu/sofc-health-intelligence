import numpy as np
import pandas as pd

from sofc_health.validation.metrics import interval_metrics, regression_metrics
from sofc_health.validation.splits import leave_one_cell_out, rolling_origin_splits


def test_leave_one_cell_out_never_overlaps_cells() -> None:
    frame = pd.DataFrame({"cell_id": ["N1", "N1", "N2", "N2"], "assessment_index": [1, 2, 1, 2]})

    for fold in leave_one_cell_out(frame):
        train_cells = set(frame.loc[fold.train_indices, "cell_id"])
        test_cells = set(frame.loc[fold.test_indices, "cell_id"])
        assert train_cells.isdisjoint(test_cells)


def test_rolling_origin_preserves_time_and_gap() -> None:
    frame = pd.DataFrame({"cell_id": ["N1"] * 8, "assessment_index": range(1, 9)})
    folds = list(
        rolling_origin_splits(frame, cell_id="N1", min_train_assessments=3, horizon=2, gap=1)
    )

    for fold in folds:
        train_max = frame.loc[fold.train_indices, "assessment_index"].max()
        test_min = frame.loc[fold.test_indices, "assessment_index"].min()
        assert test_min - train_max == 2


def test_metrics_report_bias_and_interval_coverage() -> None:
    metrics = regression_metrics(np.array([1.0, 2.0]), np.array([2.0, 2.0]))
    intervals = interval_metrics(np.array([1.0, 2.0]), np.array([0.5, 1.5]), np.array([1.5, 2.5]))

    assert metrics["mae"] == 0.5
    assert metrics["bias"] == 0.5
    assert intervals == {"coverage": 1.0, "mean_interval_width": 1.0}
