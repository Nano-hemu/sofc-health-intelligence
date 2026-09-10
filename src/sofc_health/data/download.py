"""Download and safely extract the source dataset."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path, PurePosixPath

import pooch

from sofc_health.config import DATASET


def download_archive(raw_dir: Path, *, progressbar: bool = True) -> Path:
    """Download the immutable archive and verify its SHA-256 digest."""

    raw_dir.mkdir(parents=True, exist_ok=True)
    archive = pooch.retrieve(
        url=str(DATASET.url),
        known_hash=f"sha256:{DATASET.sha256}",
        fname=DATASET.archive_name,
        path=raw_dir,
        progressbar=progressbar,
    )
    return Path(archive)


def _safe_members(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    """Return non-junk members after rejecting path traversal entries."""

    safe: list[zipfile.ZipInfo] = []
    for member in archive.infolist():
        path = PurePosixPath(member.filename)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"Unsafe archive member: {member.filename}")
        if "__MACOSX" in path.parts or any(part.startswith(".") for part in path.parts):
            continue
        safe.append(member)
    return safe


def extract_archive(archive_path: Path, raw_dir: Path) -> Path:
    """Extract once into ``data/raw/source`` and return the dataset root."""

    destination = raw_dir / "source"
    marker = destination / ".extraction_complete"
    dataset_root = destination / "SOFC_Redox_datasets"

    if marker.exists() and dataset_root.exists():
        return dataset_root
    if destination.exists() and any(destination.iterdir()):
        raise RuntimeError(
            f"Partial extraction found at {destination}. Inspect it before retrying."
        )

    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        for member in _safe_members(archive):
            target = destination / PurePosixPath(member.filename)
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, target.open("wb") as sink:
                shutil.copyfileobj(source, sink)

    if not dataset_root.exists():
        raise FileNotFoundError("Expected SOFC_Redox_datasets directory was not extracted.")
    marker.write_text(f"sha256:{DATASET.sha256}\n", encoding="utf-8")
    return dataset_root


def fetch_dataset(raw_dir: Path, *, progressbar: bool = True) -> Path:
    """Download, verify, extract, and return the source-data root."""

    return extract_archive(download_archive(raw_dir, progressbar=progressbar), raw_dir)
