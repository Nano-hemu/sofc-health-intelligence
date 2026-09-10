"""Assemble one row per cell and degradation assessment."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pandas as pd

from sofc_health.features.eis import extract_eis_features
from sofc_health.features.iv import extract_iv_features
from sofc_health.features.transient import extract_transient_features

Extractor = Callable[[pd.DataFrame], dict[str, float]]


def _summarize(frame: pd.DataFrame, extractor: Extractor) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for (cell_id, assessment), group in frame.groupby(["cell_id", "assessment_index"], sort=True):
        rows.append(
            {
                "cell_id": str(cell_id),
                "assessment_index": int(str(assessment)),
                **extractor(group),
            }
        )
    return pd.DataFrame(rows)


def build_feature_table(processed_dir: Path, output_path: Path | None = None) -> pd.DataFrame:
    """Build and optionally persist the multimodal assessment-level feature table."""

    inputs = {
        "eis": (pd.read_parquet(processed_dir / "eis.parquet"), extract_eis_features),
        "iv": (pd.read_parquet(processed_dir / "iv.parquet"), extract_iv_features),
        "transient": (
            pd.read_parquet(processed_dir / "transient.parquet"),
            extract_transient_features,
        ),
    }
    summaries = [_summarize(frame, extractor) for frame, extractor in inputs.values()]
    features = summaries[0]
    for summary in summaries[1:]:
        features = features.merge(
            summary, on=["cell_id", "assessment_index"], how="outer", validate="one_to_one"
        )
    features = features.sort_values(["cell_id", "assessment_index"]).reset_index(drop=True)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        features.to_parquet(output_path, index=False, compression="zstd")
    return features
