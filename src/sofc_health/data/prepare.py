"""Build analysis-ready Parquet tables from the source MATLAB archive."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from sofc_health.config import DATASET
from sofc_health.data.loaders import SignalType, discover_records, load_record


def _write_parquet_atomic(frame: pd.DataFrame, destination: Path) -> None:
    temporary = destination.with_suffix(".parquet.tmp")
    frame.to_parquet(temporary, index=False, compression="zstd")
    temporary.replace(destination)


def prepare_dataset(dataset_root: Path, output_dir: Path) -> dict[str, Any]:
    """Normalize every source file and write one Parquet table per signal type."""

    output_dir.mkdir(parents=True, exist_ok=True)
    records = discover_records(dataset_root)
    grouped: dict[SignalType, list[pd.DataFrame]] = defaultdict(list)
    file_counts: Counter[str] = Counter()
    repaired_files: list[str] = []

    for record in records:
        frame = load_record(record)
        grouped[record.signal_type].append(frame)
        file_counts[record.signal_type] += 1
        if bool(frame["schema_repaired"].iloc[0]):
            repaired_files.append(record.source_file)

    row_counts: dict[str, int] = {}
    schemas: dict[str, list[str]] = {}
    for signal_type in ("eis", "iv", "transient"):
        frame = pd.concat(grouped[signal_type], ignore_index=True)
        frame = frame.sort_values(
            ["cell_id", "assessment_index", "sample_index"], kind="stable"
        ).reset_index(drop=True)
        _write_parquet_atomic(frame, output_dir / f"{signal_type}.parquet")
        row_counts[signal_type] = len(frame)
        schemas[signal_type] = list(frame.columns)

    manifest: dict[str, Any] = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "dataset": {
            "title": DATASET.title,
            "doi": DATASET.doi,
            "sha256": DATASET.sha256,
            "licence": DATASET.licence,
        },
        "cells": list(DATASET.expected_cells),
        "source_file_count": len(records),
        "source_files_by_signal": dict(sorted(file_counts.items())),
        "rows_by_signal": row_counts,
        "schemas": schemas,
        "schema_repaired_files": repaired_files,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
