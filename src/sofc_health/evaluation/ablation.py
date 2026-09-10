"""Modality-ablation definitions for measuring information contribution."""

from __future__ import annotations

import pandas as pd

MODALITY_PREFIXES = {
    "eis": "eis_",
    "iv": "iv_",
    "transient": "tr_",
}


def modality_feature_sets(frame: pd.DataFrame) -> dict[str, list[str]]:
    """Return full, single-modality, and leave-one-modality-out feature sets."""

    columns = [str(column) for column in frame.columns]
    by_modality = {
        name: sorted(column for column in columns if column.startswith(prefix))
        for name, prefix in MODALITY_PREFIXES.items()
    }
    all_features = sorted({column for columns in by_modality.values() for column in columns})
    sets = {"all_modalities": all_features}
    sets.update({f"only_{name}": columns for name, columns in by_modality.items()})
    for name, columns in by_modality.items():
        sets[f"without_{name}"] = sorted(set(all_features) - set(columns))
    return sets
