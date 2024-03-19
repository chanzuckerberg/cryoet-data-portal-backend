from typing import Any, Callable

import pytest as pytest
from tests.db_import.populate_db import populate_run

import common.db_models as models


@pytest.fixture
def dataset_30001_tiltseries_expected(http_prefix: str) -> list[dict[str, Any]]:
    return [
        {
            "id": 2,
            "run_id": 2,
            "s3_mrc_bin1": "s3://test-public-bucket/30001/RUN1/TiltSeries/ts_foo.mrc",
            "https_mrc_bin1": f"{http_prefix}/30001/RUN1/TiltSeries/ts_foo.mrc",
            "s3_omezarr_dir": "s3://test-public-bucket/30001/RUN1/TiltSeries/ts_foo.zarr",
            "https_omezarr_dir": f"{http_prefix}/30001/RUN1/TiltSeries/ts_foo.zarr",
            "s3_collection_metadata": "s3://test-public-bucket/30001/RUN1/TiltSeries/foo.mdoc",
            "https_collection_metadata": f"{http_prefix}/30001/RUN1/TiltSeries/foo.mdoc",
            "s3_angle_list": "s3://test-public-bucket/30001/RUN1/TiltSeries/bar.rawtlt",
            "https_angle_list": f"{http_prefix}/30001/RUN1/TiltSeries/bar.rawtlt",
            "s3_alignment_file": "s3://test-public-bucket/30001/RUN1/TiltSeries/baz.xf",
            "https_alignment_file": f"{http_prefix}/30001/RUN1/TiltSeries/baz.xf",
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
            "tilt_min": -40,
            "tilt_max": 40,
            "tilt_range": 80,
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
            "id": 3,
            "run_id": 4,
            "s3_mrc_bin1": "s3://test-public-bucket/30001/RUN3/TiltSeries/ts_foo.mrc",
            "https_mrc_bin1": f"{http_prefix}/30001/RUN1/TiltSeries/ts_foo.mrc",
            "s3_omezarr_dir": "s3://test-public-bucket/30001/RUN1/TiltSeries/ts_foo.zarr",
            "https_omezarr_dir": f"{http_prefix}/30001/RUN1/TiltSeries/ts_foo.zarr",
            "s3_angle_list": "s3://test-public-bucket/30001/RUN3/TiltSeries/bar.tlt",
            "https_angle_list": f"{http_prefix}/30001/RUN3/TiltSeries/bar.tlt",
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


def populate_tiltseries():
    models.TiltSeries(
        id=2,
        run_id=2,
        s3_mrc_bin1="ts_foo.mrc",
        https_mrc_bin1="ts_foo.mrc",
        s3_omezarr_dir="ts_foo.zarr",
        https_omezarr_dir="ts_foo.zarr",
        acceleration_voltage=100,
        spherical_aberration_constant=1.0,
        microscope_manufacturer="unknown",
        microscope_model="unknown",
        microscope_energy_filter="unknown",
        camera_manufacturer="unknown",
        camera_model="unknown",
        tilt_min=0,
        tilt_max=0,
        tilt_range=0,
        tilt_step=0,
        tilt_axis=1.0,
        tilt_series_quality=3,
        total_flux=0,
        is_aligned=False,
        pixel_spacing=0.3,
        tilting_scheme="unknown",
        data_acquisition_software="unknown",
    ).save(force_insert=True)


# Tests addition of new tiltseries, and updating entries already existing in db
def test_import_tiltseries(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    dataset_30001_tiltseries_expected: list[dict[str, Any]],
) -> None:
    populate_run()
    populate_tiltseries()
    actual = verify_dataset_import(["--import-tiltseries"])
    expected = iter(dataset_30001_tiltseries_expected)
    for run in actual.runs:
        for tiltseries in run.tiltseries:
            verify_model(tiltseries, next(expected))
