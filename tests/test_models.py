import numpy as np

from sofc_health.models.baselines import drift, persistence
from sofc_health.models.uncertainty import conformal_interval, conformal_radius


def test_persistence_and_drift_are_distinct_baselines() -> None:
    history = np.array([100.0, 98.0, 96.0])

    assert persistence(history, 2).tolist() == [96.0, 96.0]
    assert drift(history, 2).tolist() == [94.0, 92.0]


def test_conformal_interval_uses_calibration_residuals() -> None:
    actual = np.array([10.0, 10.0, 10.0, 10.0])
    predicted = np.array([9.0, 11.0, 8.0, 12.0])
    radius = conformal_radius(actual, predicted, alpha=0.25)
    lower, upper = conformal_interval(np.array([9.0]), radius)

    assert radius == 2.0
    assert lower.tolist() == [7.0]
    assert upper.tolist() == [11.0]
