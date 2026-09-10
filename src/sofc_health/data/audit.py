"""Quality checks for the normalized SOFC tables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from sofc_health.config import DATASET


def _duplicate_key_count(frame: pd.DataFrame, signal_type: str) -> int:
    coordinate = "frequency_hz" if signal_type == "eis" else "elapsed_s"
    keys = ["cell_id", "assessment_index", coordinate]
    return int(frame.duplicated(keys).sum())


def audit_dataset(processed_dir: Path) -> dict[str, Any]:
    """Return machine-readable coverage, missingness, and key-integrity checks."""

    report: dict[str, Any] = {
        "expected_cells": list(DATASET.expected_cells),
        "signals": {},
        "passed": True,
    }

    for signal_type in ("eis", "iv", "transient"):
        path = processed_dir / f"{signal_type}.parquet"
        if not path.exists():
            raise FileNotFoundError(f"Missing processed table: {path}")
        frame = pd.read_parquet(path)
        observed_cells = sorted(frame["cell_id"].unique().tolist())
        missing_cells = sorted(set(DATASET.expected_cells) - set(observed_cells))
        missing_values = int(frame.isna().sum().sum())
        duplicate_keys = _duplicate_key_count(frame, signal_type)
        assessments = (
            frame[["cell_id", "assessment_index"]]
            .drop_duplicates()
            .groupby("cell_id")["assessment_index"]
            .nunique()
            .astype(int)
            .to_dict()
        )
        signal_report = {
            "rows": len(frame),
            "columns": list(frame.columns),
            "observed_cells": observed_cells,
            "missing_cells": missing_cells,
            "assessments_by_cell": assessments,
            "missing_values": missing_values,
            "duplicate_coordinate_keys": duplicate_keys,
            "schema_repaired_source_files": sorted(
                frame.loc[frame["schema_repaired"], "source_file"].unique().tolist()
            ),
        }
        report["signals"][signal_type] = signal_report
        if missing_cells or missing_values or duplicate_keys:
            report["passed"] = False

    return report


def write_audit(processed_dir: Path, destination: Path | None = None) -> dict[str, Any]:
    """Run the audit and persist it as JSON."""

    report = audit_dataset(processed_dir)
    output = destination or processed_dir / "audit_report.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
