from typing import Any, Callable

import pytest as pytest

import common.db_models as models


@pytest.fixture
def dataset_30001_voxel_spacings_expected(http_prefix: str) -> list[dict[str, Any]]:
    return [
        {
            "id": 2,
            "run_id": 2,
            "voxel_spacing": 12.3,
            "s3_prefix": "s3://test-public-bucket/30001/RUN1/Tomograms/VoxelSpacing12.300/",
            "https_prefix": f"{http_prefix}/30001/RUN1/Tomograms/VoxelSpacing12.300/",
        },
        {
            "id": 3,
            "run_id": 2,
            "voxel_spacing": 3.456,
            "s3_prefix": "s3://test-public-bucket/30001/RUN1/Tomograms/VoxelSpacing3.456/",
            "https_prefix": f"{http_prefix}/30001/RUN1/Tomograms/VoxelSpacing3.456/",
        },
    ]


# Tests addition of new voxel_spacings, and updating entries already existing in db
def test_import_voxel_spacings(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    dataset_30001_voxel_spacings_expected: list[dict[str, Any]],
) -> None:
    actual = verify_dataset_import(["--import-tomograms"])
    expected = iter(dataset_30001_voxel_spacings_expected)
    for run in actual.runs:
        for tomogram_voxel_spacing in run.tomogram_voxel_spacings:
            verify_model(tomogram_voxel_spacing, next(expected))
