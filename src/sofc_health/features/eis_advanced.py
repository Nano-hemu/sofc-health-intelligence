"""Optional Lin-KK, equivalent-circuit, and DRT analysis for EIS spectra."""

from __future__ import annotations

import contextlib
import io
from typing import Any

import numpy as np
import pandas as pd


def _complex_spectrum(group: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    frame = group[["frequency_hz", "z_real_ohm", "z_imag_ohm"]].dropna()
    frame = frame[frame["frequency_hz"] > 0].sort_values("frequency_hz", ascending=False)
    if len(frame) < 12:
        raise ValueError("Advanced EIS analysis requires at least twelve frequencies")
    frequency = frame["frequency_hz"].to_numpy(dtype=float)
    impedance = frame["z_real_ohm"].to_numpy(dtype=float) + 1j * frame["z_imag_ohm"].to_numpy(
        dtype=float
    )
    return frequency, impedance


def lin_kk_diagnostics(group: pd.DataFrame, *, max_elements: int = 50) -> dict[str, float]:
    """Return linear Kramers–Kronig fit diagnostics using the impedance package."""

    from impedance.models.circuits.elements import circuit_elements
    from impedance.validation import linKK

    frequency, impedance = _complex_spectrum(group)
    # impedance.py 1.7.1 serializes NumPy scalars as ``np.float64(...)`` inside
    # its evaluator under NumPy 2.x, but does not expose NumPy to that evaluator.
    circuit_elements.setdefault("np", np)
    with contextlib.redirect_stdout(io.StringIO()):
        elements, mu, fitted, residual_real, residual_imag = linKK(
            frequency,
            impedance,
            c=0.85,
            max_M=max_elements,
            fit_type="complex",
            add_cap=False,
        )
    relative_rmse = np.sqrt(np.mean(np.abs(impedance - fitted) ** 2)) / np.sqrt(
        np.mean(np.abs(impedance) ** 2)
    )
    return {
        "lin_kk_elements": float(elements),
        "lin_kk_mu": float(mu),
        "lin_kk_relative_rmse": float(relative_rmse),
        "lin_kk_max_abs_real_residual_pct": float(np.max(np.abs(residual_real))),
        "lin_kk_max_abs_imag_residual_pct": float(np.max(np.abs(residual_imag))),
    }


def fit_equivalent_circuit(
    group: pd.DataFrame,
    *,
    circuit: str = "R0-p(R1,CPE1)",
    initial_guess: tuple[float, ...] = (0.2, 1.0, 0.01, 0.8),
) -> dict[str, float]:
    """Fit a declared circuit and return parameters plus normalized residual error.

    A successful numerical fit is not proof of physical identifiability. Compare alternate
    circuits, parameter confidence, residual structure, and cross-assessment stability.
    """

    from impedance.models.circuits import CustomCircuit

    frequency, impedance = _complex_spectrum(group)
    model = CustomCircuit(circuit, initial_guess=list(initial_guess))
    model.fit(frequency, impedance)
    fitted = np.asarray(model.predict(frequency), dtype=complex)
    names, _ = model.get_param_names()
    parameters = {
        f"ecm_{name.lower()}": float(value)
        for name, value in zip(names, model.parameters_, strict=True)
    }
    parameters["ecm_relative_rmse"] = float(
        np.sqrt(np.mean(np.abs(impedance - fitted) ** 2)) / np.sqrt(np.mean(np.abs(impedance) ** 2))
    )
    return parameters


def drt_summary(
    group: pd.DataFrame,
    *,
    method: str = "tr-nnls",
    peak_threshold: float = 0.05,
    **kwargs: Any,
) -> dict[str, float]:
    """Calculate a DRT and summarize peak count, dominant timescale, and total intensity."""

    import pyimpspec

    frequency, impedance = _complex_spectrum(group)
    dataset = pyimpspec.DataSet(frequency=frequency, impedance=impedance)
    result = pyimpspec.calculate_drt(
        dataset,
        method=method,
        mode="complex",
        inductance=True,
        **kwargs,
    )
    tau, gamma = result.get_drt_data()
    peak_tau, peak_gamma = result.get_peaks(threshold=peak_threshold)
    dominant = int(np.argmax(gamma))
    return {
        "drt_peak_count": float(len(peak_tau)),
        "drt_dominant_tau_s": float(tau[dominant]),
        "drt_dominant_gamma_ohm": float(gamma[dominant]),
        "drt_total_intensity_ohm": float(np.trapezoid(gamma, np.log(tau))),
        "drt_largest_detected_peak_ohm": (
            float(np.max(peak_gamma)) if len(peak_gamma) else float("nan")
        ),
    }
