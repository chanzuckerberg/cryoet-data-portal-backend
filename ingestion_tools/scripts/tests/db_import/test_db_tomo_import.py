from typing import Any, Callable

import pytest as pytest
from tests.db_import.populate_db import (
    DATASET_ID,
    RUN_ID,
    TOMOGRAM_AUTHOR_ID,
    TOMOGRAM_ID,
    TOMOGRAM_VOXEL_ID,
    populate_tomogram_authors_table,
    populate_tomograms_table,
)

import common.db_models as models


@pytest.fixture
def expected_voxel_spacings(http_prefix: str) -> list[dict[str, Any]]:
    return [
        {
            "id": 103,
            "run_id": RUN_ID,
            "voxel_spacing": 3.456,
            "s3_prefix": f"s3://test-public-bucket/{DATASET_ID}/RUN1/Tomograms/VoxelSpacing3.456/",
            "https_prefix": "http://test.com/RUN1/VoxelSpacing3.456/",
        },
        {
            "id": TOMOGRAM_VOXEL_ID,
            "run_id": RUN_ID,
            "voxel_spacing": 12.3,
            "s3_prefix": f"s3://test-public-bucket/{DATASET_ID}/RUN1/Tomograms/VoxelSpacing12.300/",
            "https_prefix": f"{http_prefix}/{DATASET_ID}/RUN1/Tomograms/VoxelSpacing12.300/",
        },
        {
            "voxel_spacing": 3.456,
            "s3_prefix": f"s3://test-public-bucket/{DATASET_ID}/RUN2/Tomograms/VoxelSpacing3.456/",
            "https_prefix": f"{http_prefix}/{DATASET_ID}/RUN2/Tomograms/VoxelSpacing3.456/",
        },
    ]


@pytest.fixture
def expected_tomograms(http_prefix: str) -> list[dict[str, Any]]:
    run1_vs_path = f"{DATASET_ID}/RUN1/Tomograms/VoxelSpacing12.300/"
    run2_vs_path = f"{DATASET_ID}/RUN2/Tomograms/VoxelSpacing3.456/"
    return [
        {
            "id": TOMOGRAM_ID,
            "tomogram_voxel_spacing_id": TOMOGRAM_VOXEL_ID,
            "name": "RUN1",
            "size_x": 980,
            "size_y": 1016,
            "size_z": 500,
            "voxel_spacing": 12.3,
            "fiducial_alignment_status": "FIDUCIAL",
            "reconstruction_method": "Weighted back projection",
            "reconstruction_software": "IMOD",
            "processing": "raw",
            "processing_software": "tomo3D",
            "tomogram_version": "1",
            "is_canonical": True,
            "s3_omezarr_dir": f"s3://test-public-bucket/{run1_vs_path}CanonicalTomogram/RUN1.zarr",
            "https_omezarr_dir": f"{http_prefix}/{run1_vs_path}CanonicalTomogram/RUN1.zarr",
            "s3_mrc_scale0": f"s3://test-public-bucket/{run1_vs_path}CanonicalTomogram/RUN1.mrc",
            "https_mrc_scale0": f"{http_prefix}/{run1_vs_path}CanonicalTomogram/RUN1.mrc",
            "scale0_dimensions": "980,1016,500",
            "scale1_dimensions": "490,508,250",
            "scale2_dimensions": "245,254,125",
            "ctf_corrected": True,
            "offset_x": 10,
            "offset_y": 32,
            "offset_z": 43,
            "affine_transformation_matrix": [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ],
            "key_photo_url": f"{http_prefix}/{run1_vs_path}KeyPhotos/key-photo-snapshot.png",
            "key_photo_thumbnail_url": f"{http_prefix}/{run1_vs_path}KeyPhotos/key-photo-thumbnail.png",
            "neuroglancer_config": '{"foo":"bar","baz":"test"}',
            "type": "CANONICAL",
        },
        {
            "name": "RUN2",
            "size_x": 800,
            "size_y": 800,
            "size_z": 400,
            "voxel_spacing": 3.456,
            "fiducial_alignment_status": "NON_FIDUCIAL",
            "reconstruction_method": "None",
            "reconstruction_software": "None",
            "processing": "filtered",
            "tomogram_version": "1",
            "is_canonical": True,
            "s3_omezarr_dir": f"s3://test-public-bucket/{run2_vs_path}CanonicalTomogram/RUN2.zarr",
            "https_omezarr_dir": f"{http_prefix}/{run2_vs_path}CanonicalTomogram/RUN2.zarr",
            "s3_mrc_scale0": f"s3://test-public-bucket/{run2_vs_path}CanonicalTomogram/RUN2.mrc",
            "https_mrc_scale0": f"{http_prefix}/{run2_vs_path}CanonicalTomogram/RUN2.mrc",
            "scale0_dimensions": "800,800,400",
            "scale1_dimensions": "400,400,200",
            "scale2_dimensions": "200,200,100",
            "ctf_corrected": False,
            "offset_x": 0,
            "offset_y": 0,
            "offset_z": 0,
            "neuroglancer_config": "{}",
            "type": "CANONICAL",
        },
    ]


@pytest.fixture
def expected_tomograms_authors() -> list[list[dict[str, Any]]]:
    return [
        [
            {
                "tomogram_id": TOMOGRAM_ID,
                "name": "John Doe",
                "corresponding_author_status": True,
                "primary_author_status": False,
                "author_list_order": 1,
            },
            {
                "id": TOMOGRAM_AUTHOR_ID,
                "tomogram_id": TOMOGRAM_ID,
                "orcid": "0000-4444-1234-0000",
                "name": "Jane Smith",
                "corresponding_author_status": False,
                "primary_author_status": False,
                "email": "jsmith@test.com",
                "affiliation_name": "Foo",
                "affiliation_address": "some address",
                "affiliation_identifier": "test-affliation-id",
                "author_list_order": 2,
            },
        ],
        [],
    ]


# Tests addition of new voxel_spacings, and updating entries already existing in db
def test_import_voxel_spacings_and_tomograms(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    expected_voxel_spacings: list[dict[str, Any]],
    expected_tomograms: list[dict[str, Any]],
) -> None:
    populate_tomograms_table()
    actual = verify_dataset_import(["--import-tomograms"])
    expected_voxel_spacings_iter = iter(expected_voxel_spacings)
    expected_tomograms_iter = iter(expected_tomograms)
    for run in actual.runs:
        for tomogram_voxel_spacing in run.tomogram_voxel_spacings.order_by(models.TomogramVoxelSpacing.voxel_spacing):
            expected_voxel_spacing = next(expected_voxel_spacings_iter)
            if "run_id" not in expected_voxel_spacing:
                expected_voxel_spacing["run_id"] = run.id
            verify_model(tomogram_voxel_spacing, expected_voxel_spacing)
            for tomogram in tomogram_voxel_spacing.tomograms:
                expected_tomogram = next(expected_tomograms_iter)
                if "tomogram_voxel_spacing_id" not in expected_tomogram:
                    expected_tomogram["tomogram_voxel_spacing_id"] = tomogram_voxel_spacing.id
                verify_model(tomogram, expected_tomogram)
                assert len(tomogram.authors) == 0


# Tests addition of new tomogram_author
def test_import_tomograms_authors(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    expected_tomograms_authors: list[list[dict[str, Any]]],
) -> None:
    populate_tomogram_authors_table()
    actual = verify_dataset_import(["--import-tomogram-authors"])
    expected_tomograms_authors_iter = iter(expected_tomograms_authors)
    for run in actual.runs:
        for tomogram_voxel_spacing in run.tomogram_voxel_spacings:
            for tomogram in tomogram_voxel_spacing.tomograms:
                tomogram_authors = next(expected_tomograms_authors_iter)
                assert len(tomogram.authors) == len(tomogram_authors)
                tomogram_authors_iter = iter(tomogram_authors)
                for author in tomogram.authors.order_by(models.TomogramAuthor.author_list_order):
                    verify_model(author, next(tomogram_authors_iter))
