import zipfile
from pathlib import Path

import pytest

from sofc_health.data.download import _safe_members


def test_safe_members_rejects_zip_slip(tmp_path: Path) -> None:
    archive_path = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("../escape.txt", "unsafe")

    with (
        zipfile.ZipFile(archive_path) as archive,
        pytest.raises(ValueError, match="Unsafe archive member"),
    ):
        _safe_members(archive)


def test_safe_members_skips_operating_system_metadata(tmp_path: Path) -> None:
    archive_path = tmp_path / "metadata.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("__MACOSX/junk", "junk")
        archive.writestr("SOFC_Redox_datasets/N1/value.mat", "data")

    with zipfile.ZipFile(archive_path) as archive:
        names = [member.filename for member in _safe_members(archive)]

    assert names == ["SOFC_Redox_datasets/N1/value.mat"]
