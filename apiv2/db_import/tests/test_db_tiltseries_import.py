from typing import Any, Callable

import pytest as pytest
from database import models
from db_import.tests.populate_db import (
    DATASET_ID,
    RUN1_ID,
    TILTSERIES_ID,
    populate_stale_run,
    populate_stale_tiltseries,
    populate_tiltseries,
)
from sqlalchemy.orm import Session

from platformics.database.models import Base


@pytest.fixture
def expected_tiltseries(http_prefix: str) -> list[dict[str, Any]]:
    return [
        {
            "acceleration_voltage": 300000,
            "aligned_tiltseries_binning": 3,
            "binning_from_frames": 1,
            "camera_manufacturer": "Gatan",
            "camera_model": "K2 Summit",
            "data_acquisition_software": "SerialEM",
            "deposition_id": 300,
            "https_angle_list": f"{http_prefix}/{DATASET_ID}/RUN1/TiltSeries/100/bar.rawtlt",
            "https_mrc_file": f"{http_prefix}/{DATASET_ID}/RUN1/TiltSeries/100/ts_foo.mrc",
            "https_omezarr_dir": f"{http_prefix}/{DATASET_ID}/RUN1/TiltSeries/100/ts_foo.zarr",
            "id": TILTSERIES_ID,
            "is_aligned": True,
            "microscope_additional_info": "info about the scope",
            "microscope_energy_filter": "GIF Quantum LS",
            "microscope_image_corrector": "Foo",
            "microscope_manufacturer": "TFS",
            "microscope_model": "Krios",
            "microscope_phase_plate": "Volta Phase Plate",
            "pixel_spacing": 4.370,
            "related_empiar_entry": "EMPIAR-XYZ",
            "run_id": RUN1_ID,
            "s3_angle_list": f"s3://test-public-bucket/{DATASET_ID}/RUN1/TiltSeries/100/bar.rawtlt",
            "s3_mrc_file": f"s3://test-public-bucket/{DATASET_ID}/RUN1/TiltSeries/100/ts_foo.mrc",
            "s3_omezarr_dir": f"s3://test-public-bucket/{DATASET_ID}/RUN1/TiltSeries/100/ts_foo.zarr",
            "spherical_aberration_constant": 2.7,
            "tilt_axis": 84.7,
            "tilt_max": 40.97,
            "tilt_min": -40.01,
            "tilt_range": 80.98,
            "tilt_series_quality": 5,
            "tilt_step": 2,
            "tilting_scheme": "Dose symmetric from 0.0 degrees",
            "total_flux": 122,
        },
        {
            "acceleration_voltage": 10000,
            "camera_manufacturer": "FEI",
            "camera_model": "FALCON",
            "data_acquisition_software": "leginon",
            "deposition_id": 300,
            "https_angle_list": f"{http_prefix}/{DATASET_ID}/RUN3/TiltSeries/100/bar.tlt",
            "https_mrc_file": f"{http_prefix}/{DATASET_ID}/RUN3/TiltSeries/100/ts_foo.mrc",
            "https_omezarr_dir": f"{http_prefix}/{DATASET_ID}/RUN3/TiltSeries/100/ts_foo.zarr",
            "is_aligned": False,
            "microscope_energy_filter": "TFS",
            "microscope_manufacturer": "FEI",
            "microscope_model": "Phantom",
            "pixel_spacing": 5.240,
            "s3_angle_list": f"s3://test-public-bucket/{DATASET_ID}/RUN3/TiltSeries/100/bar.tlt",
            "s3_mrc_file": f"s3://test-public-bucket/{DATASET_ID}/RUN3/TiltSeries/100/ts_foo.mrc",
            "s3_omezarr_dir": f"s3://test-public-bucket/{DATASET_ID}/RUN3/TiltSeries/100/ts_foo.zarr",
            "spherical_aberration_constant": 2.7,
            "tilt_axis": 56.4,
            "tilt_max": 33,
            "tilt_min": -33,
            "tilt_range": 66,
            "tilt_series_quality": 2,
            "tilt_step": 3,
            "tilting_scheme": "min to max tilt",
            "total_flux": 12,
        },
    ]


# Tests addition of new tiltseries, and updating entries already existing in db
def test_import_tiltseries(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_tiltseries: list[dict[str, Any]],
) -> None:
    populate_tiltseries(sync_db_session)
    sync_db_session.commit()
    actual = verify_dataset_import(import_tiltseries=True)
    expected_iter = iter(expected_tiltseries)
    for run in sorted(actual.runs, key=lambda x: x.name):
        for tiltseries in run.tiltseries:
            expected = next(expected_iter)
            if "run_id" not in expected:
                expected["run_id"] = run.id
            verify_model(tiltseries, expected)


# Tests addition of new tiltseries, and updating entries already existing in db
def test_import_tiltseries_stale_deletion(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_tiltseries: list[dict[str, Any]],
) -> None:
    populate_tiltseries(sync_db_session)
    populate_stale_run(sync_db_session)
    populate_stale_tiltseries(sync_db_session)
    sync_db_session.commit()
    actual = verify_dataset_import(import_tiltseries=True)
    expected_iter = iter(expected_tiltseries)
    for run in sorted(actual.runs, key=lambda x: x.name):
        for tiltseries in run.tiltseries:
            expected = next(expected_iter)
            if "run_id" not in expected:
                expected["run_id"] = run.id
            verify_model(tiltseries, expected)
