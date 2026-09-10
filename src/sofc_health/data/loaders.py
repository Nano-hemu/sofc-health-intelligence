"""Load MATLAB table objects and normalize inconsistent source schemas."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import matio
import numpy as np
import pandas as pd

SignalType = Literal["eis", "iv", "transient"]

_CELL_PATTERN = re.compile(r"^[NR]\d+$")
_INDEX_PATTERN = re.compile(r"(\d+)$")
_SIGNAL_ORDER: dict[SignalType, int] = {"eis": 0, "iv": 1, "transient": 2}


@dataclass(frozen=True)
class SourceRecord:
    """Identity of one measurement table in the source archive."""

    cell_id: str
    signal_type: SignalType
    assessment_index: int
    path: Path

    @property
    def source_file(self) -> str:
        return f"{self.cell_id}/{self.path.parent.name}/{self.path.name}"


def parse_source_record(path: Path) -> SourceRecord:
    """Infer cell, signal type, and assessment index from a source path."""

    cell_candidates = [part for part in path.parts if _CELL_PATTERN.fullmatch(part)]
    if len(cell_candidates) != 1:
        raise ValueError(f"Cannot identify exactly one cell in {path}")

    parent = path.parent.name.lower()
    if parent == "eis_curves":
        signal_type: SignalType = "eis"
    elif parent == "iv_curves":
        signal_type = "iv"
    elif "dynamics" in parent:  # Covers Transient_dynamics and source typo Transinet_dynamics.
        signal_type = "transient"
    else:
        raise ValueError(f"Unknown measurement directory: {path.parent.name}")

    index_match = _INDEX_PATTERN.search(path.stem)
    if index_match is None:
        raise ValueError(f"No assessment index in {path.name}")

    return SourceRecord(
        cell_id=cell_candidates[0],
        signal_type=signal_type,
        assessment_index=int(index_match.group(1)),
        path=path,
    )


def discover_records(dataset_root: Path) -> list[SourceRecord]:
    """Discover all measurement files in deterministic physical order."""

    records = [parse_source_record(path) for path in dataset_root.rglob("*.mat")]
    return sorted(
        records,
        key=lambda item: (
            item.cell_id[0],
            int(item.cell_id[1:]),
            _SIGNAL_ORDER[item.signal_type],
            item.assessment_index,
        ),
    )


def load_mat_table(path: Path) -> pd.DataFrame:
    """Decode a MATLAB table using mat-io and return a defensive copy."""

    variables = matio.load_from_mat(str(path))
    tables = [value for value in variables.values() if isinstance(value, pd.DataFrame)]
    if len(tables) != 1:
        raise ValueError(f"Expected one MATLAB table in {path}; found {len(tables)}")
    return tables[0].copy()


def _column_key(name: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def _numeric(frame: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {column: pd.to_numeric(frame[column], errors="coerce") for column in frame.columns},
        index=frame.index,
    )


def _normalize_eis(raw: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    aliases = {
        "freqhz": "frequency_hz",
        "ampl": "amplitude_v",
        "bias": "bias_v",
        "timesec": "elapsed_s",
        "za": "z_real_ohm",
        "zb": "z_imag_ohm",
        "gd": "gd",
        "err": "error_code",
        "range": "range_code",
    }
    rename = {column: aliases.get(_column_key(column), str(column)) for column in raw.columns}
    frame = _numeric(raw.rename(columns=rename))
    required = ["frequency_hz", "z_real_ohm", "z_imag_ohm"]
    missing = [column for column in required if column not in frame]
    if missing:
        raise ValueError(f"EIS table missing columns: {missing}")
    frame = frame.dropna(subset=required)
    frame = frame[frame["frequency_hz"] > 0].reset_index(drop=True)
    return frame, False


def _normalize_iv_like(raw: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    aliases = {
        "evolts": "voltage_v",
        "iacm2": "current_density_a_cm2",
        "tseconds": "elapsed_s",
    }
    keys = {_column_key(column) for column in raw.columns}
    standard_schema = set(aliases).issubset(keys)

    if standard_schema:
        rename = {column: aliases.get(_column_key(column), str(column)) for column in raw.columns}
        frame = _numeric(raw.rename(columns=rename))[
            ["voltage_v", "current_density_a_cm2", "elapsed_s"]
        ]
    else:
        if raw.shape[1] < 3:
            raise ValueError("IV-like table has fewer than three columns")
        frame = _numeric(raw.iloc[:, :3].copy())
        frame.columns = ["voltage_v", "current_density_a_cm2", "elapsed_s"]

    frame = frame.dropna().copy()
    plausible = (
        frame["voltage_v"].between(0.3, 1.5)
        & frame["current_density_a_cm2"].between(-5.0, 5.0)
        & frame["elapsed_s"].between(0.0, 1.0e7)
    )
    frame = frame.loc[plausible].reset_index(drop=True)
    return frame, not standard_schema


def normalize_table(record: SourceRecord, raw: pd.DataFrame) -> pd.DataFrame:
    """Convert one source table to the canonical long-form schema."""

    if record.signal_type == "eis":
        frame, repaired = _normalize_eis(raw)
    else:
        frame, repaired = _normalize_iv_like(raw)

    if frame.empty:
        raise ValueError(f"No valid observations remained after cleaning {record.path}")

    frame.insert(0, "sample_index", np.arange(len(frame), dtype=np.int32))
    frame.insert(0, "source_file", record.source_file)
    frame.insert(0, "schema_repaired", repaired)
    frame.insert(0, "assessment_index", record.assessment_index)
    frame.insert(0, "signal_type", record.signal_type)
    frame.insert(0, "cell_id", record.cell_id)
    return frame


def load_record(record: SourceRecord) -> pd.DataFrame:
    """Load and normalize one source record."""

    return normalize_table(record, load_mat_table(record.path))
