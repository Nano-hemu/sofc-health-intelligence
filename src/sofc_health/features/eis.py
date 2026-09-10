"""Interpretable, circuit-agnostic features from impedance spectra."""

from __future__ import annotations

import numpy as np
import pandas as pd


def extract_eis_features(group: pd.DataFrame) -> dict[str, float]:
    """Extract robust Nyquist/Bode descriptors from one spectrum.

    The features intentionally avoid claiming an equivalent-circuit mechanism. Circuit
    parameters are only defensible after validity testing and residual diagnostics.
    """

    frame = group[["frequency_hz", "z_real_ohm", "z_imag_ohm"]].dropna().copy()
    frame = frame[frame["frequency_hz"] > 0].sort_values("frequency_hz", ascending=False)
    if len(frame) < 8:
        raise ValueError("An EIS spectrum requires at least eight valid frequencies")

    frequency = frame["frequency_hz"].to_numpy(dtype=float)
    z_real = frame["z_real_ohm"].to_numpy(dtype=float)
    z_imag = frame["z_imag_ohm"].to_numpy(dtype=float)
    high_frequency_count = max(5, len(frame) // 3)
    high_slice = slice(0, high_frequency_count)
    ohmic_index = int(np.argmin(np.abs(z_imag[high_slice])))
    r_ohmic = float(z_real[ohmic_index])

    capacitive = z_imag < 0
    if capacitive.any():
        cap_frequency = frequency[capacitive]
        cap_imag = z_imag[capacitive]
        peak_index = int(np.argmax(-cap_imag))
        peak_frequency = float(cap_frequency[peak_index])
        arc_height = float(-cap_imag[peak_index])
    else:
        peak_frequency = float("nan")
        arc_height = float("nan")

    low_frequency_real = float(np.median(z_real[-min(3, len(z_real)) :]))
    return {
        "eis_r_ohmic_ohm": r_ohmic,
        "eis_low_frequency_real_ohm": low_frequency_real,
        "eis_polarization_proxy_ohm": low_frequency_real - r_ohmic,
        "eis_arc_peak_frequency_hz": peak_frequency,
        "eis_arc_height_ohm": arc_height,
        "eis_inductive_fraction": float(np.mean(z_imag > 0)),
        "eis_log_frequency_span_decades": float(
            np.log10(frequency.max()) - np.log10(frequency.min())
        ),
        "eis_sample_count": float(len(frame)),
    }
