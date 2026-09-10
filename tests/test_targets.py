import numpy as np
import pandas as pd

from sofc_health.targets.rul import add_rul_target
from sofc_health.targets.soh import add_soh_targets


def _feature_rows() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "cell_id": ["N1"] * 4 + ["N2"] * 4,
            "assessment_index": [1, 2, 3, 4] * 2,
            "tr_performance_current_a_cm2": [1.0, 0.9, 0.79, 0.7, 2.0, 1.9, 1.8, 1.7],
            "iv_max_power_w_cm2": [0.5, 0.45, 0.39, 0.35, 1.0, 0.95, 0.9, 0.85],
            "iv_current_at_0p70v_a_cm2": [0.8, 0.72, 0.63, 0.56, 1.6, 1.52, 1.44, 1.36],
        }
    )


def test_soh_is_normalized_within_cell() -> None:
    result = add_soh_targets(_feature_rows())

    first = result.groupby("cell_id").first()
    assert np.allclose(first["soh_current_pct"], 100.0)
    assert np.allclose(first["soh_composite_pct"], 100.0)


def test_rul_marks_observed_and_censored_cells() -> None:
    result = add_rul_target(
        add_soh_targets(_feature_rows()), threshold_pct=80.0, consecutive_below=2
    )
    n1 = result[result["cell_id"] == "N1"]
    n2 = result[result["cell_id"] == "N2"]

    assert n1["eol_assessment"].iloc[0] == 3
    assert n1["rul_assessments"].tolist() == [2.0, 1.0, 0.0, 0.0]
    assert not n1["rul_right_censored"].any()
    assert n2["rul_right_censored"].all()
    assert n2["rul_assessments"].isna().all()
