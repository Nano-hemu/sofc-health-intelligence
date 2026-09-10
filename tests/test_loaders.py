from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from sofc_health.data.loaders import SourceRecord, normalize_table, parse_source_record


@pytest.mark.parametrize(
    ("relative_path", "signal_type", "assessment_index"),
    [
        ("N1/EIS_curves/EIS12.mat", "eis", 12),
        ("N4/IV_curves/IV7.mat", "iv", 7),
        ("R2/Transient_dynamics/Transient3.mat", "transient", 3),
        ("N5/Transinet_dynamics/Transient19.mat", "transient", 19),
    ],
)
def test_parse_source_record_handles_source_layout_and_typo(
    relative_path: str, signal_type: str, assessment_index: int
) -> None:
    record = parse_source_record(Path(relative_path))

    assert record.cell_id == relative_path[:2]
    assert record.signal_type == signal_type
    assert record.assessment_index == assessment_index


def test_normalize_eis_aliases_and_filters_invalid_frequency() -> None:
    raw = pd.DataFrame(
        {
            "Freq_Hz_": [1_000.0, 100.0, -1.0],
            "Ampl": [0.01, 0.01, 0.01],
            "Bias": [0.7, 0.7, 0.7],
            "Time_Sec_": [0.0, 1.0, 2.0],
            "Z__a_": [0.40, 0.50, 0.60],
            "Z___b_": [-0.08, -0.12, -0.15],
            "GD": [0, 0, 0],
            "Err": [0, 0, 0],
            "Range": [1, 1, 1],
        }
    )
    record = SourceRecord("N1", "eis", 4, Path("N1/EIS_curves/EIS4.mat"))

    result = normalize_table(record, raw)

    assert result["frequency_hz"].tolist() == [1_000.0, 100.0]
    assert result["z_real_ohm"].tolist() == [0.40, 0.50]
    assert result["z_imag_ohm"].tolist() == [-0.08, -0.12]
    assert not result["schema_repaired"].any()


def test_normalize_standard_iv_schema() -> None:
    raw = pd.DataFrame(
        {
            "E_Volts_": [1.05, 0.95],
            "I_A_cm2_": [0.0, 0.2],
            "T_Seconds_": [0.0, 0.5],
        }
    )
    record = SourceRecord("N2", "iv", 1, Path("N2/IV_curves/IV1.mat"))

    result = normalize_table(record, raw)

    assert result["voltage_v"].tolist() == [1.05, 0.95]
    assert result["current_density_a_cm2"].tolist() == [0.0, 0.2]
    assert not result["schema_repaired"].any()


def test_repair_malformed_iv_uses_numeric_rows_from_first_three_columns() -> None:
    raw = pd.DataFrame(
        {
            "Date_": ["metadata", 1.02, 0.91, 9.0],
            "unexpected": ["metadata", 0.0, 0.25, 20.0],
            "Time_": ["metadata", 0.0, 0.5, -1.0],
            "ignored": ["x", "x", "x", "x"],
        }
    )
    record = SourceRecord("N5", "iv", 13, Path("N5/IV_curves/IV13.mat"))

    result = normalize_table(record, raw)

    assert result["schema_repaired"].all()
    assert np.allclose(result["voltage_v"], [1.02, 0.91])
    assert np.allclose(result["current_density_a_cm2"], [0.0, 0.25])
    assert np.allclose(result["elapsed_s"], [0.0, 0.5])


def test_rejects_empty_table_after_physical_bounds_filter() -> None:
    raw = pd.DataFrame(
        {
            "EVolts": [8.0],
            "IAcm2": [0.1],
            "TSeconds": [0.0],
        }
    )
    record = SourceRecord("R1", "transient", 1, Path("R1/Transient_dynamics/T1.mat"))

    with pytest.raises(ValueError, match="No valid observations"):
        normalize_table(record, raw)
