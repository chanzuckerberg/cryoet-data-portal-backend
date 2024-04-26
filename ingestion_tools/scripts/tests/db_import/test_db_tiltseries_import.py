from typing import Any, Callable

import pytest as pytest
from tests.db_import.populate_db import (
    DATASET_ID,
    RUN1_ID,
    TILTSERIES_ID,
    populate_stale_run,
    populate_stale_tiltseries,
    populate_tiltseries,
)

import common.db_models as models


@pytest.fixture
def expected_tiltseries(http_prefix: str) -> list[dict[str, Any]]:
    return [
        {
            "id": TILTSERIES_ID,
            "run_id": RUN1_ID,
            "s3_mrc_bin1": f"s3://test-public-bucket/{DATASET_ID}/RUN1/TiltSeries/ts_foo.mrc",
            "https_mrc_bin1": f"{http_prefix}/{DATASET_ID}/RUN1/TiltSeries/ts_foo.mrc",
            "s3_omezarr_dir": f"s3://test-public-bucket/{DATASET_ID}/RUN1/TiltSeries/ts_foo.zarr",
            "https_omezarr_dir": f"{http_prefix}/{DATASET_ID}/RUN1/TiltSeries/ts_foo.zarr",
            "s3_collection_metadata": f"s3://test-public-bucket/{DATASET_ID}/RUN1/TiltSeries/foo.mdoc",
            "https_collection_metadata": f"{http_prefix}/{DATASET_ID}/RUN1/TiltSeries/foo.mdoc",
            "s3_angle_list": f"s3://test-public-bucket/{DATASET_ID}/RUN1/TiltSeries/bar.rawtlt",
            "https_angle_list": f"{http_prefix}/{DATASET_ID}/RUN1/TiltSeries/bar.rawtlt",
            "s3_alignment_file": f"s3://test-public-bucket/{DATASET_ID}/RUN1/TiltSeries/baz.xf",
            "https_alignment_file": f"{http_prefix}/{DATASET_ID}/RUN1/TiltSeries/baz.xf",
            "acceleration_voltage": 300000,
            "spherical_aberration_constant": 2.7,
            "microscope_manufacturer": "TFS",
            "microscope_model": "Krios",
            "microscope_energy_filter": "GIF Quantum LS",
            "microscope_phase_plate": "Volta Phase Plate",
            "microscope_image_corrector": "Foo",
            "microscope_additional_info": "info about the scope",
            "camera_manufacturer": "Gatan",
            "camera_model": "K2 Summit",
            "tilt_min": -40.01,
            "tilt_max": 40.97,
            "tilt_range": 80.98,
            "tilt_step": 2,
            "tilting_scheme": "Dose symmetric from 0.0 degrees",
            "tilt_axis": 84.7,
            "total_flux": 122,
            "data_acquisition_software": "SerialEM",
            "binning_from_frames": 1,
            "tilt_series_quality": 5,
            "related_empiar_entry": "EMPIAR-XYZ",
            "is_aligned": True,
            "aligned_tiltseries_binning": 3,
            "pixel_spacing": 4.370,
            "frames_count": 60,
        },
        {
            "s3_mrc_bin1": f"s3://test-public-bucket/{DATASET_ID}/RUN3/TiltSeries/ts_foo.mrc",
            "https_mrc_bin1": f"{http_prefix}/{DATASET_ID}/RUN3/TiltSeries/ts_foo.mrc",
            "s3_omezarr_dir": f"s3://test-public-bucket/{DATASET_ID}/RUN3/TiltSeries/ts_foo.zarr",
            "https_omezarr_dir": f"{http_prefix}/{DATASET_ID}/RUN3/TiltSeries/ts_foo.zarr",
            "s3_angle_list": f"s3://test-public-bucket/{DATASET_ID}/RUN3/TiltSeries/bar.tlt",
            "https_angle_list": f"{http_prefix}/{DATASET_ID}/RUN3/TiltSeries/bar.tlt",
            "acceleration_voltage": 10000,
            "spherical_aberration_constant": 2.7,
            "microscope_manufacturer": "DC",
            "microscope_model": "Phantom",
            "microscope_energy_filter": "TFS",
            "camera_manufacturer": "FEI",
            "camera_model": "FALCON",
            "tilt_min": -33,
            "tilt_max": 33,
            "tilt_range": 66,
            "tilt_step": 3,
            "tilting_scheme": "min to max tilt",
            "tilt_axis": 56.4,
            "total_flux": 12,
            "data_acquisition_software": "leginon",
            "tilt_series_quality": 2,
            "is_aligned": False,
            "pixel_spacing": 5.240,
        },
    ]


# Tests addition of new tiltseries, and updating entries already existing in db
def test_import_tiltseries(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    expected_tiltseries: list[dict[str, Any]],
) -> None:
    populate_tiltseries()
    actual = verify_dataset_import(["--import-tiltseries"])
    expected_iter = iter(expected_tiltseries)
    for run in actual.runs.order_by(models.Run.name):
        for tiltseries in run.tiltseries:
            expected = next(expected_iter)
            if "run_id" not in expected:
                expected["run_id"] = run.id
            verify_model(tiltseries, expected)


# Tests addition of new tiltseries, and updating entries already existing in db
def test_import_tiltseries_stale_deletion(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    expected_tiltseries: list[dict[str, Any]],
) -> None:
    populate_tiltseries()
    populate_stale_run()
    populate_stale_tiltseries()
    actual = verify_dataset_import(["--import-tiltseries"])
    expected_iter = iter(expected_tiltseries)
    for run in actual.runs.order_by(models.Run.name):
        for tiltseries in run.tiltseries:
            expected = next(expected_iter)
            if "run_id" not in expected:
                expected["run_id"] = run.id
            verify_model(tiltseries, expected)
