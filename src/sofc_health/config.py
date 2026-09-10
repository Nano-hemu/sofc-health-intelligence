"""Dataset provenance and project-wide constants."""

from pydantic import BaseModel, ConfigDict, HttpUrl


class DatasetSpec(BaseModel):
    """Immutable source-dataset contract."""

    model_config = ConfigDict(frozen=True)

    title: str
    doi: str
    url: HttpUrl
    archive_name: str
    sha256: str
    licence: str
    expected_cells: tuple[str, ...]


DATASET = DatasetSpec(
    title="Tubular SOFC under Redox Cycling Degradation",
    doi="10.7939/82178",
    url=HttpUrl(
        "https://ualberta.scholaris.ca/server/api/core/bitstreams/"
        "697e202d-aaa2-42fd-9044-81618e272978/content"
    ),
    archive_name="SOFC_Redox_datasets.zip",
    sha256="5b36aeba4794faf4982c5bb918f878294d80e417a9ff9cc0ce37e0de6dba5f26",
    licence="CC BY-NC 4.0",
    expected_cells=("N1", "N2", "N3", "N4", "N5", "N6", "R1", "R2"),
)
