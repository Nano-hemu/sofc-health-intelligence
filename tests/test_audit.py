from pathlib import Path

import pandas as pd

from sofc_health.config import DATASET
from sofc_health.data.audit import audit_dataset


def _metadata(signal_type: str) -> dict[str, object]:
    return {
        "signal_type": signal_type,
        "assessment_index": 1,
        "schema_repaired": False,
        "source_file": f"N1/{signal_type}/1.mat",
        "sample_index": 0,
    }


def test_audit_passes_complete_unique_tables(tmp_path: Path) -> None:
    cells = list(DATASET.expected_cells)
    eis = pd.DataFrame(
        [{"cell_id": cell, "frequency_hz": 1_000.0, **_metadata("eis")} for cell in cells]
    )
    iv = pd.DataFrame(
        [
            {
                "cell_id": cell,
                "elapsed_s": 0.0,
                "voltage_v": 1.0,
                "current_density_a_cm2": 0.0,
                **_metadata("iv"),
            }
            for cell in cells
        ]
    )
    transient = iv.assign(signal_type="transient")
    eis.to_parquet(tmp_path / "eis.parquet", index=False)
    iv.to_parquet(tmp_path / "iv.parquet", index=False)
    transient.to_parquet(tmp_path / "transient.parquet", index=False)

    report = audit_dataset(tmp_path)

    assert report["passed"] is True
    assert report["signals"]["eis"]["observed_cells"] == cells


def test_audit_fails_duplicate_measurement_coordinate(tmp_path: Path) -> None:
    cells = list(DATASET.expected_cells)
    eis_rows = [{"cell_id": cell, "frequency_hz": 1_000.0, **_metadata("eis")} for cell in cells]
    eis = pd.concat([pd.DataFrame(eis_rows), pd.DataFrame([eis_rows[0]])], ignore_index=True)
    iv = pd.DataFrame(
        [
            {
                "cell_id": cell,
                "elapsed_s": 0.0,
                "voltage_v": 1.0,
                "current_density_a_cm2": 0.0,
                **_metadata("iv"),
            }
            for cell in cells
        ]
    )
    eis.to_parquet(tmp_path / "eis.parquet", index=False)
    iv.to_parquet(tmp_path / "iv.parquet", index=False)
    iv.assign(signal_type="transient").to_parquet(tmp_path / "transient.parquet", index=False)

    report = audit_dataset(tmp_path)

    assert report["passed"] is False
    assert report["signals"]["eis"]["duplicate_coordinate_keys"] == 1
