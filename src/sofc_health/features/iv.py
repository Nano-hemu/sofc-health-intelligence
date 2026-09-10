"""Features from SOFC polarization (IV) curves."""

from __future__ import annotations

import numpy as np
import pandas as pd

from sofc_health.features.common import finite_xy, interpolate_if_supported, linear_slope

REFERENCE_CURRENTS_A_CM2 = (0.10, 0.20, 0.30)


def extract_iv_features(group: pd.DataFrame) -> dict[str, float]:
    """Extract interpretable performance and resistance proxies from one IV curve."""

    voltage = group["voltage_v"].to_numpy(dtype=float)
    load_current = -group["current_density_a_cm2"].to_numpy(dtype=float)
    current, voltage = finite_xy(load_current, voltage)
    if current.size < 5:
        raise ValueError("An IV curve requires at least five valid points")

    nonnegative = current >= 0
    current, voltage = current[nonnegative], voltage[nonnegative]
    if current.size < 5:
        raise ValueError("An IV curve has insufficient fuel-cell-mode points")
    power = current * voltage
    near_linear = (current >= 0.05) & (current <= min(0.30, float(current.max())))
    asr_proxy = -linear_slope(current[near_linear], voltage[near_linear])

    features = {
        "iv_ocv_v": float(voltage[np.argmin(np.abs(current))]),
        "iv_max_current_a_cm2": float(current.max()),
        "iv_max_power_w_cm2": float(power.max()),
        "iv_current_at_0p70v_a_cm2": interpolate_if_supported(voltage[::-1], current[::-1], 0.70),
        "iv_asr_proxy_ohm_cm2": asr_proxy,
        "iv_sample_count": float(current.size),
    }
    for reference in REFERENCE_CURRENTS_A_CM2:
        label = str(reference).replace(".", "p")
        features[f"iv_voltage_at_{label}a_cm2_v"] = interpolate_if_supported(
            current, voltage, reference
        )
    return features
