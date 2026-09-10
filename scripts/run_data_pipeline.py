"""Explicit Python entry point equivalent to ``sofc-health all``."""

from pathlib import Path

from sofc_health.data.audit import write_audit
from sofc_health.data.download import fetch_dataset
from sofc_health.data.prepare import prepare_dataset
from sofc_health.features.build import build_feature_table
from sofc_health.targets.rul import add_rul_target
from sofc_health.targets.soh import add_soh_targets


def main() -> None:
    raw_dir = Path("data/raw")
    processed_dir = Path("data/processed")
    source = fetch_dataset(raw_dir)
    prepare_dataset(source, processed_dir)
    report = write_audit(processed_dir)
    if not report["passed"]:
        raise RuntimeError("Data-quality audit failed")
    features = build_feature_table(processed_dir, processed_dir / "features.parquet")
    modeling = add_rul_target(add_soh_targets(features))
    modeling.to_parquet(processed_dir / "modeling_table.parquet", index=False, compression="zstd")


if __name__ == "__main__":
    main()
