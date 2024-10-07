from datetime import date
from typing import Any, Callable

import pytest as pytest
from database import models
from db_import.tests.populate_db import (
    DATASET_ID,
    DEPOSITION_ID2,
    RUN1_ID,
    TOMOGRAM_AUTHOR_ID,
    TOMOGRAM_ID,
    TOMOGRAM_VOXEL_ID1,
    TOMOGRAM_VOXEL_ID2,
    populate_stale_tomogram_authors,
    populate_stale_tomogram_voxel_spacing,
    populate_stale_tomograms,
    populate_tomogram_authors,
    populate_tomograms,
)
from sqlalchemy.orm import Session

from platformics.database.models import Base


@pytest.fixture
def expected_voxel_spacings_by_run(http_prefix: str) -> dict[str, list[dict[str, Any]]]:
    run1_voxel_spacings = [
        {
            "id": TOMOGRAM_VOXEL_ID2,
            "run_id": RUN1_ID,
            "voxel_spacing": 9.876,
            "s3_prefix": f"s3://test-public-bucket/{DATASET_ID}/RUN1/Tomograms/VoxelSpacing9.876/",
            "https_prefix": f"{http_prefix}/{DATASET_ID}/RUN1/Tomograms/VoxelSpacing9.876/",
        },
        {
            "id": TOMOGRAM_VOXEL_ID1,
            "run_id": RUN1_ID,
            "voxel_spacing": 12.3,
            "s3_prefix": f"s3://test-public-bucket/{DATASET_ID}/RUN1/Tomograms/VoxelSpacing12.300/",
            "https_prefix": f"{http_prefix}/{DATASET_ID}/RUN1/Tomograms/VoxelSpacing12.300/",
        },
    ]
    run2_voxel_spacings = [
        {
            "voxel_spacing": 3.456,
            "s3_prefix": f"s3://test-public-bucket/{DATASET_ID}/RUN2/Tomograms/VoxelSpacing3.456/",
            "https_prefix": f"{http_prefix}/{DATASET_ID}/RUN2/Tomograms/VoxelSpacing3.456/",
        },
    ]
    return {
        "RUN1": run1_voxel_spacings,
        "RUN2": run2_voxel_spacings,
    }


@pytest.fixture
def expected_tomograms_by_run(http_prefix: str) -> dict[str, dict[float, list[dict[str, Any]]]]:
    run1_vs_path = f"{DATASET_ID}/RUN1/Tomograms/VoxelSpacing12.300/"
    run2_vs_path = f"{DATASET_ID}/RUN2/Tomograms/VoxelSpacing3.456/"
    run1_tomo = {
        "id": TOMOGRAM_ID,
        "tomogram_voxel_spacing_id": TOMOGRAM_VOXEL_ID1,
        "name": "RUN1",
        "size_x": 980,
        "size_y": 1016,
        "size_z": 500,
        "voxel_spacing": 12.3,
        "fiducial_alignment_status": "FIDUCIAL",
        "reconstruction_method": "WBP",
        "reconstruction_software": "IMOD",
        "processing": "raw",
        "processing_software": "tomo3D",
        "tomogram_version": 1.0,
        "s3_omezarr_dir": f"s3://test-public-bucket/{run1_vs_path}CanonicalTomogram/RUN1.zarr",
        "https_omezarr_dir": f"{http_prefix}/{run1_vs_path}CanonicalTomogram/RUN1.zarr",
        "s3_mrc_file": f"s3://test-public-bucket/{run1_vs_path}CanonicalTomogram/RUN1.mrc",
        "https_mrc_file": f"{http_prefix}/{run1_vs_path}CanonicalTomogram/RUN1.mrc",
        "scale0_dimensions": "980,1016,500",
        "scale1_dimensions": "490,508,250",
        "scale2_dimensions": "245,254,125",
        "ctf_corrected": True,
        "offset_x": 10,
        "offset_y": 32,
        "offset_z": 43,
        "key_photo_url": f"{http_prefix}/{run1_vs_path}KeyPhotos/key-photo-snapshot.png",
        "key_photo_thumbnail_url": f"{http_prefix}/{run1_vs_path}KeyPhotos/key-photo-thumbnail.png",
        "neuroglancer_config": '{"foo":"bar","baz":"test"}',
        "deposition_id": 301,
        "is_portal_standard": False,
        "is_canonical": False,
        "deposition_date": date(2023, 4, 2),
        "release_date": date(2024, 6, 1),
        "last_modified_date": date(2023, 9, 2),
    }
    run2_tomo = {
        "name": "RUN2",
        "size_x": 800,
        "size_y": 800,
        "size_z": 400,
        "voxel_spacing": 3.456,
        "fiducial_alignment_status": "NON_FIDUCIAL",
        "reconstruction_method": "SART",
        "reconstruction_software": "Unknown",
        "processing": "filtered",
        "tomogram_version": 1.0,
        "s3_omezarr_dir": f"s3://test-public-bucket/{run2_vs_path}CanonicalTomogram/RUN2.zarr",
        "https_omezarr_dir": f"{http_prefix}/{run2_vs_path}CanonicalTomogram/RUN2.zarr",
        "s3_mrc_file": f"s3://test-public-bucket/{run2_vs_path}CanonicalTomogram/RUN2.mrc",
        "https_mrc_file": f"{http_prefix}/{run2_vs_path}CanonicalTomogram/RUN2.mrc",
        "scale0_dimensions": "800,800,400",
        "scale1_dimensions": "400,400,200",
        "scale2_dimensions": "200,200,100",
        "ctf_corrected": False,
        "offset_x": 0,
        "offset_y": 0,
        "offset_z": 0,
        "neuroglancer_config": "{}",
        "deposition_id": 300,
        "is_portal_standard": False,
        "is_canonical": False,
        "deposition_date": date(2022, 4, 2),
        "release_date": date(2022, 6, 1),
        "last_modified_date": date(2022, 9, 2),
    }
    return {
        "RUN1": {
            12.300: [run1_tomo],
        },
        "RUN2": {
            3.456: [run2_tomo],
        },
    }


@pytest.fixture
def expected_tomograms_authors_by_run() -> dict[str, dict[float, list[dict[str, Any]]]]:
    return {
        "RUN1": {
            12.300: [
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
        },
    }


# Tests addition of new voxel_spacings, and updating entries already existing in db
def test_import_voxel_spacings_and_tomograms(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_voxel_spacings_by_run: dict[str, list[dict[str, Any]]],
    expected_tomograms_by_run: dict[str, dict[float, list[dict[str, Any]]]],
) -> None:
    populate_tomograms(sync_db_session)
    sync_db_session.commit()
    actual = verify_dataset_import(import_tomograms=True, import_depositions=True, deposition_id=[DEPOSITION_ID2])
    for run in sorted(actual.runs, key=lambda x: x.name):
        tomogram_voxel_spacings = sorted(run.tomogram_voxel_spacings, key=lambda x: x.voxel_spacing)
        expected_voxel_spacings = expected_voxel_spacings_by_run.get(run.name, [])
        assert len(tomogram_voxel_spacings) == len(expected_voxel_spacings)

        expected_voxel_spacings_iter = iter(expected_voxel_spacings)
        for actual_tvs in tomogram_voxel_spacings:
            expected_voxel_spacing = next(expected_voxel_spacings_iter)
            if "run_id" not in expected_voxel_spacing:
                expected_voxel_spacing["run_id"] = run.id
            verify_model(actual_tvs, expected_voxel_spacing)

            expected_tomograms = expected_tomograms_by_run.get(run.name, {}).get(actual_tvs.voxel_spacing, [])
            assert len(actual_tvs.tomograms) == len(expected_tomograms)
            expected_tomograms_iter = iter(expected_tomograms)
            for tomogram in actual_tvs.tomograms:
                expected_tomogram = next(expected_tomograms_iter)
                if "tomogram_voxel_spacing_id" not in expected_tomogram:
                    expected_tomogram["tomogram_voxel_spacing_id"] = actual_tvs.id
                verify_model(tomogram, expected_tomogram)
                assert len(tomogram.authors) == 0


# Tests addition of new, and update of existing tomogram authors
def test_import_tomograms_authors(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_tomograms_authors_by_run: dict[str, dict[float, list[dict[str, Any]]]],
) -> None:
    populate_tomogram_authors(sync_db_session)
    sync_db_session.commit()
    actual = verify_dataset_import(import_tomogram_authors=True)
    for run in sorted(actual.runs, key=lambda x: x.name):
        for tomogram_voxel_spacing in sorted(run.tomogram_voxel_spacings, key=lambda x: x.voxel_spacing):
            for tomogram in tomogram_voxel_spacing.tomograms:
                expected_tomogram_authors = expected_tomograms_authors_by_run.get(run.name, {}).get(
                    tomogram_voxel_spacing.voxel_spacing,
                    [],
                )
                assert len(tomogram.authors) == len(expected_tomogram_authors)
                tomogram_authors_iter = iter(expected_tomogram_authors)
                for author in sorted(tomogram.authors, key=lambda x: x.author_list_order):
                    verify_model(author, next(tomogram_authors_iter))


# Tests deletion of stale voxel spacing, tomograms and tomogram authors
def test_import_voxel_spacings_tomograms_and_authors_removes_stale(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_voxel_spacings_by_run: dict[str, list[dict[str, Any]]],
    expected_tomograms_by_run: dict[str, dict[float, list[dict[str, Any]]]],
    expected_tomograms_authors_by_run: dict[str, dict[float, list[dict[str, Any]]]],
) -> None:
    populate_tomogram_authors(sync_db_session)
    populate_stale_tomogram_voxel_spacing(sync_db_session)
    populate_stale_tomograms(sync_db_session)
    populate_stale_tomogram_authors(sync_db_session)
    sync_db_session.commit()
    actual = verify_dataset_import(import_tomogram_authors=True)

    for run in sorted(actual.runs, key=lambda x: x.name):
        tomogram_voxel_spacings = sorted(run.tomogram_voxel_spacings, key=lambda x: x.voxel_spacing)
        expected_voxel_spacings = expected_voxel_spacings_by_run.get(run.name, [])
        assert len(tomogram_voxel_spacings) == len(expected_voxel_spacings)

        expected_voxel_spacings_iter = iter(expected_voxel_spacings)
        for actual_tvs in tomogram_voxel_spacings:
            expected_voxel_spacing = next(expected_voxel_spacings_iter)
            if "run_id" not in expected_voxel_spacing:
                expected_voxel_spacing["run_id"] = run.id
            verify_model(actual_tvs, expected_voxel_spacing)

            expected_tomograms = expected_tomograms_by_run.get(run.name, {}).get(actual_tvs.voxel_spacing, [])
            assert len(actual_tvs.tomograms) == len(expected_tomograms)
            expected_tomograms_iter = iter(expected_tomograms)
            for tomogram in actual_tvs.tomograms:
                expected_tomogram = next(expected_tomograms_iter)
                if "tomogram_voxel_spacing_id" not in expected_tomogram:
                    expected_tomogram["tomogram_voxel_spacing_id"] = actual_tvs.id
                verify_model(tomogram, expected_tomogram)

                expected_tomogram_authors = expected_tomograms_authors_by_run.get(run.name, {}).get(
                    actual_tvs.voxel_spacing,
                    [],
                )
                assert len(tomogram.authors) == len(expected_tomogram_authors)
                tomogram_authors_iter = iter(expected_tomogram_authors)
                for author in sorted(tomogram.authors, key=lambda x: x.author_list_order):
                    verify_model(author, next(tomogram_authors_iter))
