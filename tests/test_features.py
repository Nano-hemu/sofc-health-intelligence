import numpy as np
import pandas as pd

from sofc_health.features.eis import extract_eis_features
from sofc_health.features.iv import extract_iv_features
from sofc_health.features.transient import extract_transient_features


def test_transient_features_recover_steady_state_and_response_time() -> None:
    time_s = np.arange(0.0, 101.0)
    current = -0.6 * (1.0 - np.exp(-time_s / 10.0))
    frame = pd.DataFrame({"elapsed_s": time_s, "current_density_a_cm2": current})

    features = extract_transient_features(frame)

    assert 0.59 < features["tr_performance_current_a_cm2"] < 0.61
    assert 20.0 <= features["tr_t90_s"] <= 27.0
    assert features["tr_duration_s"] == 100.0


def test_iv_features_interpolate_at_physical_reference() -> None:
    load_current = np.linspace(0.0, 0.5, 51)
    voltage = 1.1 - 0.8 * load_current
    frame = pd.DataFrame({"voltage_v": voltage, "current_density_a_cm2": -load_current})

    features = extract_iv_features(frame)

    assert np.isclose(features["iv_ocv_v"], 1.1)
    assert np.isclose(features["iv_current_at_0p70v_a_cm2"], 0.5)
    assert np.isclose(features["iv_asr_proxy_ohm_cm2"], 0.8)


def test_eis_features_keep_inductive_behavior_visible() -> None:
    frequency = np.logspace(5, -1, 61)
    z_real = np.linspace(0.2, 1.2, 61)
    z_imag = -0.3 * np.sin(np.linspace(0.0, np.pi, 61))
    z_imag[:3] = 0.02
    frame = pd.DataFrame({"frequency_hz": frequency, "z_real_ohm": z_real, "z_imag_ohm": z_imag})

    features = extract_eis_features(frame)

    assert features["eis_r_ohmic_ohm"] < 0.3
    assert features["eis_polarization_proxy_ohm"] > 0.8
    assert features["eis_inductive_fraction"] > 0
