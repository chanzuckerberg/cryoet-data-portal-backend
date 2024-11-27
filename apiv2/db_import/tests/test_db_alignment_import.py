from typing import Any, Callable

import pytest as pytest
from database import models
from db_import.tests.populate_db import (
    DATASET_ID,
    RUN1_ID,
    TILTSERIES_ID,
    populate_alignments,
    populate_per_section_alignment_parameters,
    populate_stale_alignments,
    populate_stale_per_section_alignment_parameters,
    populate_stale_run,
)
from sqlalchemy.orm import Session

from platformics.database.models.base import Base


@pytest.fixture
def expected_alignments(http_prefix: str) -> list[dict[str, Any]]:
    return [
        {
            "id": 801,
            "run_id": RUN1_ID,
            "tiltseries_id": TILTSERIES_ID,
            "deposition_id": 300,
            "alignment_method": "patch_tracking",
            "alignment_type": "GLOBAL",
            "volume_x_dimension": 900,
            "volume_y_dimension": 908,
            "volume_z_dimension": 500,
            "volume_x_offset": 0,
            "volume_y_offset": 0,
            "volume_z_offset": 0,
            "tilt_offset": 0,
            "x_rotation_offset": 0,
            "affine_transformation_matrix": "{{1,0,0,0},{0,1,0,0},{0,0,1,0},{0,0,0,1}}",
            "s3_alignment_metadata": f"s3://test-public-bucket/{DATASET_ID}/RUN1/Alignments/100/alignment_metadata.json",
            "https_alignment_metadata": f"{http_prefix}/{DATASET_ID}/RUN1/Alignments/100/alignment_metadata.json",
            "is_portal_standard": False,
        },
    ]


@pytest.fixture
def expected_per_section_alignment_parameters() -> list[dict[str, Any]]:
    return [
        {
            "in_plane_rotation": [0.1, 0.2, -0.3, 0.4],
            "x_offset": -4.345,
            "y_offset": 5.789,
            "z_index": 0,
            "tilt_angle": None,
            "volume_x_rotation": 0.0,
        },
        {
            "in_plane_rotation": [0.33, 0.44, -0.55, 0.66],
            "x_offset": -3.21,
            "y_offset": 4.321,
            "z_index": 1,
            "tilt_angle": None,
            "volume_x_rotation": 0.0,
        },
    ]


def test_import_alignments(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_alignments: list[dict[str, Any]],
) -> None:
    populate_alignments(sync_db_session)
    sync_db_session.commit()
    actual = verify_dataset_import(import_alignments=True)
    expected_iter = iter(expected_alignments)
    for run in sorted(actual.runs, key=lambda x: x.name):
        for alignment in run.alignments:
            expected = next(expected_iter)
            if "run_id" not in expected:
                expected["run_id"] = run.id
            verify_model(alignment, expected)


def test_import_alignments_stale_deletion(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_alignments: list[dict[str, Any]],
) -> None:
    populate_alignments(sync_db_session)
    populate_stale_run(sync_db_session)
    populate_stale_alignments(sync_db_session)
    sync_db_session.commit()
    actual = verify_dataset_import(import_alignments=True)
    expected_iter = iter(expected_alignments)
    for run in sorted(actual.runs, key=lambda x: x.name):
        for alignment in run.alignments:
            expected = next(expected_iter)
            if "run_id" not in expected:
                expected["run_id"] = run.id
            verify_model(alignment, expected)


def test_import_per_section_alignment_parameters(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_per_section_alignment_parameters: list[dict[str, Any]],
) -> None:
    populate_per_section_alignment_parameters(sync_db_session)
    sync_db_session.commit()
    actual = verify_dataset_import(import_alignments=True)
    expected_per_section_alignments_iter = iter(expected_per_section_alignment_parameters)

    for run in sorted(actual.runs, key=lambda x: x.name):
        for tiltseries in run.tiltseries:
            for alignment in tiltseries.alignments:
                for per_section_alignment in alignment.per_section_alignments:
                    expected = next(expected_per_section_alignments_iter)
                    if "alignment_id" not in expected:
                        expected["alignment_id"] = alignment.id
                    verify_model(per_section_alignment, expected)


def test_import_per_section_alignment_parameters_stale_deletion(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_per_section_alignment_parameters: list[dict[str, Any]],
) -> None:
    populate_per_section_alignment_parameters(sync_db_session)
    populate_stale_run(sync_db_session)
    populate_stale_per_section_alignment_parameters(sync_db_session)
    sync_db_session.commit()
    actual = verify_dataset_import(import_alignments=True)
    expected_per_section_alignments_iter = iter(expected_per_section_alignment_parameters)
    for run in sorted(actual.runs, key=lambda x: x.name):
        for tiltseries in run.tiltseries:
            for alignment in tiltseries.alignments:
                for per_section_alignment in alignment.per_section_alignments:
                    expected = next(expected_per_section_alignments_iter)
                    if "alignment_id" not in expected:
                        expected["alignment_id"] = alignment.id
                    verify_model(per_section_alignment, expected)
