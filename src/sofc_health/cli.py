"""Command-line interface for reproducible dataset preparation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import pandas as pd
import typer
from rich.console import Console

from sofc_health.data.audit import write_audit
from sofc_health.data.download import fetch_dataset
from sofc_health.data.prepare import prepare_dataset
from sofc_health.features.build import build_feature_table
from sofc_health.targets.rul import add_rul_target
from sofc_health.targets.soh import add_soh_targets

app = typer.Typer(no_args_is_help=True, help="SOFC Health Intelligence data pipeline.")
console = Console()

RawOption = Annotated[Path, typer.Option(help="Directory for source data.")]
ProcessedOption = Annotated[Path, typer.Option(help="Directory for normalized tables.")]


@app.command()
def download(raw_dir: RawOption = Path("data/raw")) -> None:
    """Download, checksum, and safely extract the source dataset."""

    root = fetch_dataset(raw_dir)
    console.print(f"Dataset ready: {root}")


@app.command()
def prepare(
    raw_dir: RawOption = Path("data/raw"),
    processed_dir: ProcessedOption = Path("data/processed"),
) -> None:
    """Convert MATLAB tables to canonical Parquet tables."""

    dataset_root = raw_dir / "source" / "SOFC_Redox_datasets"
    if not dataset_root.exists():
        raise typer.BadParameter("Source data missing; run `sofc-health download` first.")
    manifest = prepare_dataset(dataset_root, processed_dir)
    console.print_json(json.dumps(manifest))


@app.command()
def audit(processed_dir: ProcessedOption = Path("data/processed")) -> None:
    """Audit coverage, schemas, nulls, and duplicate coordinates."""

    report = write_audit(processed_dir)
    console.print_json(json.dumps(report))
    if not report["passed"]:
        raise typer.Exit(code=1)


@app.command("features")
def features_command(processed_dir: ProcessedOption = Path("data/processed")) -> None:
    """Build one physics-aware feature row per cell and assessment."""

    destination = processed_dir / "features.parquet"
    features = build_feature_table(processed_dir, destination)
    console.print(f"Wrote {len(features):,} assessment rows: {destination}")


@app.command("targets")
def targets_command(
    processed_dir: ProcessedOption = Path("data/processed"),
    threshold_pct: Annotated[
        float, typer.Option(help="SOH threshold used for assessment-based RUL.")
    ] = 80.0,
) -> None:
    """Add auditable SOH candidates and censored RUL labels."""

    features_path = processed_dir / "features.parquet"
    if not features_path.exists():
        raise typer.BadParameter("Feature table missing; run `sofc-health features` first.")
    features = pd.read_parquet(features_path)
    modeling = add_rul_target(add_soh_targets(features), threshold_pct=threshold_pct)
    destination = processed_dir / "modeling_table.parquet"
    modeling.to_parquet(destination, index=False, compression="zstd")
    console.print(f"Wrote {len(modeling):,} modeling rows: {destination}")


@app.command("all")
def run_all(
    raw_dir: RawOption = Path("data/raw"),
    processed_dir: ProcessedOption = Path("data/processed"),
) -> None:
    """Run download, preparation, and audit in sequence."""

    dataset_root = fetch_dataset(raw_dir)
    manifest = prepare_dataset(dataset_root, processed_dir)
    report = write_audit(processed_dir)
    features = build_feature_table(processed_dir, processed_dir / "features.parquet")
    modeling = add_rul_target(add_soh_targets(features))
    modeling.to_parquet(processed_dir / "modeling_table.parquet", index=False, compression="zstd")
    console.print(
        f"Prepared {sum(manifest['rows_by_signal'].values()):,} rows; "
        f"audit passed={report['passed']}; {len(modeling):,} modeling rows."
    )
    if not report["passed"]:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
