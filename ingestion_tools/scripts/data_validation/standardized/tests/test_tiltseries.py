import math
import os
from typing import Any, Dict

import allure
import numpy as np
import pandas as pd
import pytest
from data_validation.shared.helper.angles_helper import helper_angles_injection_errors
from data_validation.shared.helper.tiltseries_helper import TiltSeriesHelper
from data_validation.shared.util import BINNING_FACTORS
from data_validation.standardized.tests.test_deposition import HelperTestDeposition
from mrcfile.mrcinterpreter import MrcInterpreter

MAX_DEVIATING_INCREMENTS = 4


# By setting this scope to session, scope="session" fixtures will be reinitialized for each run + voxel_spacing combination
@pytest.mark.tiltseries
@pytest.mark.parametrize(
    "dataset, run_name, ts_dir", pytest.cryoet.dataset_run_tiltseries_combinations, scope="session",
)
class TestTiltseries(TiltSeriesHelper):

    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_zarr_header_class_variables(
        self,
        tiltseries_mrc_header: Dict[str, MrcInterpreter],
        tiltseries_zarr_metadata: Dict[str, Dict[str, Dict]],
        tiltseries_metadata: Dict,
    ):
        self.mrc_headers = tiltseries_mrc_header
        self.zarr_headers = tiltseries_zarr_metadata
        self.spacing = tiltseries_metadata["pixel_spacing"]
        self.skip_z_axis_checks = True

    ### BEGIN metadata self-consistency tests ###
    @allure.title("Tiltseries: sanity check tiltseries metadata.")
    def test_metadata(self, tiltseries_metadata: Dict, run_name: str):
        assert tiltseries_metadata["acceleration_voltage"] > 0
        assert tiltseries_metadata["spherical_aberration_constant"] > 0
        assert tiltseries_metadata["tilting_scheme"]
        assert tiltseries_metadata["total_flux"] > 0
        assert tiltseries_metadata["run_name"] == run_name

    @allure.title("Tiltseries: valid corresponding deposition metadata.")
    def test_deposition_id(self, tiltseries_metadata: Dict, bucket, filesystem):
        HelperTestDeposition.check_deposition_metadata(tiltseries_metadata["deposition_id"], bucket, filesystem)

    @allure.title("Tiltseries: metadata size is consistent with scales.")
    def test_size_scales(self, tiltseries_metadata: Dict):
        assert tiltseries_metadata["size"] == tiltseries_metadata["scales"][0]

    @allure.title("Tiltseries: metadata scales is self-consistent.")
    def test_scales(self, tiltseries_metadata: Dict):
        # z size is not scaled, stays consistent
        assert len({scale["z"] for scale in tiltseries_metadata["scales"]}) == 1

        curr_scale = tiltseries_metadata["scales"][0]
        for scale in tiltseries_metadata["scales"][1:]:
            assert math.ceil(curr_scale["y"] / 2) == scale["y"]
            assert math.ceil(curr_scale["x"] / 2) == scale["x"]
            curr_scale = scale

    ### END metadata self-consistency tests ###

    ### BEGIN metadata-MRC/Zarr consistency tests ###
    @allure.title("Tiltseries: metadata volume size is consistent with MRC header.")
    def test_size_in_mrc(self, tiltseries_metadata: Dict):
        def check_size_in_mrc(header, _interpreter, _mrc_filename, tiltseries_metadata):
            del _interpreter, _mrc_filename
            assert header.nx == tiltseries_metadata["size"]["x"]
            assert header.ny == tiltseries_metadata["size"]["y"]
            assert header.nz == tiltseries_metadata["size"]["z"]

        self.mrc_header_helper(check_size_in_mrc, tiltseries_metadata=tiltseries_metadata)

    @allure.title("Tiltseries: metadata scaled volume sizes is consistent with Zarr header.")
    def test_scales_in_zarr(self, tiltseries_metadata: Dict):
        def check_size_in_zarr(header_data, _zarr_filename, tiltseries_metadata):
            del _zarr_filename
            for binning_factor in BINNING_FACTORS:  # Check all binning factors
                assert header_data["zarrays"][binning_factor]["shape"] == [
                    tiltseries_metadata["scales"][binning_factor]["z"],
                    tiltseries_metadata["scales"][binning_factor]["y"],
                    tiltseries_metadata["scales"][binning_factor]["x"],
                ]

        self.zarr_header_helper(check_size_in_zarr, tiltseries_metadata=tiltseries_metadata)

    @allure.title("Tiltseries: metadata Zarr file matches the actual file.")
    def test_zarr_matches(
        self,
        tiltseries_metadata: Dict,
        tiltseries_zarr_metadata: Dict[str, Dict[str, Dict]],
    ):
        assert len(tiltseries_zarr_metadata) == 1
        assert os.path.basename(tiltseries_metadata["omezarr_dir"]) == os.path.basename(
            list(tiltseries_zarr_metadata.keys())[0],
        )

    @allure.title("Tiltseries: metadata MRC file matches the actual file.")
    def test_mrc_matches(
        self,
        tiltseries_metadata: Dict,
        tiltseries_mrc_header: Dict[str, MrcInterpreter],
    ):
        assert len(tiltseries_mrc_header) == 1
        assert os.path.basename(tiltseries_metadata["mrc_file"]) == os.path.basename(
            list(tiltseries_mrc_header.keys())[0],
        )

    ### END metadata-MRC/Zarr consistency tests ###

    ### BEGIN metadata-mdoc consistency tests ###
    @allure.title("Mdoc: number of mdoc tilt angles equals tiltseries size['z'].")
    def test_mdoc_tiltseries_metadata(self, tiltseries_metadata: dict, mdoc_data: pd.DataFrame):
        assert len(mdoc_data) >= tiltseries_metadata["size"]["z"]

    @allure.title("Mdoc: mdoc tilt angles are consistent with tilt_range and tilt_step metadata.")
    @allure.description("Checks that the min/max of mdoc angles match tilt_range and that increments between consecutive angles match tilt_step.")
    def test_mdoc_tiltseries_range(
        self,
        tiltseries_metadata: dict,
        mdoc_data: pd.DataFrame,
    ):
        from data_validation.shared.helper.angles_helper import ANGLE_TOLERANCE

        tilt_step = tiltseries_metadata["tilt_step"]
        tilt_min = tiltseries_metadata["tilt_range"]["min"]
        tilt_max = tiltseries_metadata["tilt_range"]["max"]
        mdoc_angles = sorted(mdoc_data["TiltAngle"].to_list())

        fatal_errors = []

        # Check min and max
        if abs(mdoc_angles[0] - tilt_min) >= ANGLE_TOLERANCE:
            fatal_errors.append(f"Min mdoc angle {mdoc_angles[0]} does not match tilt_range min {tilt_min} (tolerance {ANGLE_TOLERANCE}).")
        if abs(mdoc_angles[-1] - tilt_max) >= ANGLE_TOLERANCE:
            fatal_errors.append(f"Max mdoc angle {mdoc_angles[-1]} does not match tilt_range max {tilt_max} (tolerance {ANGLE_TOLERANCE}).")

        # Check increments between consecutive angles
        increment_errors = []
        increments = {}
        for i in range(len(mdoc_angles) - 1):
            start_angle = mdoc_angles[i]
            end_angle = mdoc_angles[i + 1]
            increments[(start_angle, end_angle)] = end_angle - start_angle

        for (start_angle, end_angle), increment in increments.items():
            if abs(increment - tilt_step) >= ANGLE_TOLERANCE:
                increment_errors.append(
                    f"Increment from {start_angle} to {end_angle} is {increment}, expected tilt_step {tilt_step} (tolerance {ANGLE_TOLERANCE}).",
                )

        # Always log increment deviations as warnings
        if increment_errors:
            allure.attach(
                "\n".join(increment_errors),
                name=f"Increment deviations ({len(increment_errors)} found)",
                attachment_type=allure.attachment_type.TEXT,
            )

        # Fail if min/max mismatch or more than 4 deviating increments
        if len(increment_errors) > MAX_DEVIATING_INCREMENTS:
            fatal_errors.extend(increment_errors)

        range_info = f"\nRange: {tilt_min} to {tilt_max}, with step {tilt_step}"
        assert len(fatal_errors) == 0, "\n".join(fatal_errors) + range_info

    ### END metadata-mdoc consistency tests ###

    @allure.title("Tiltseries: sum of exposureDose of all frames associated with a tilt series == totalFlux +-1 of tilt series")
    def test_exposure_dose(self, frame_metadata: Dict, tiltseries_metadata: Dict):
        assert sum(f.get("exposure_dose", 0) for f in frame_metadata["frames"]) == pytest.approx(tiltseries_metadata["total_flux"], abs=1)

    @allure.title("PerSectionParameters: number of frames >= # of per section parameters.")
    def test_per_section_parameter_with_num_frames(self, tiltseries_metadata: dict[str, Any], frame_metadata: dict[str, dict]):
        num_frames = len(frame_metadata["frames"])
        num_per_section_parameters = len(tiltseries_metadata["per_section_parameter"])
        assert num_frames >= num_per_section_parameters, f"Number of frames {num_frames} is less than number of per section parameters {num_per_section_parameters}."

    @allure.title("PerSectionParameters: -180 <= astigmatic_angle <= 180.")
    def test_astigmatic_angle(self, tiltseries_metadata: dict[str, Any]):
        errors = []
        for i, per_section_parameter in enumerate(tiltseries_metadata["per_section_parameter"]):
            astigmatic_angle = per_section_parameter["astigmatic_angle"]
            if astigmatic_angle is None:
                continue
            try:
                assert -180 <= astigmatic_angle <= 180
            except AssertionError:
                errors.append(f"per_section_parameter[{i}].astigmatic_angle= {astigmatic_angle} is out of range [-180, 180].")
        if len(errors) > 0:
            raise AssertionError("\n".join(errors))

    @allure.title("PerSectionParameters: 0 <= phaseShift <= 2*pi.")
    def test_phase_shift(self, tiltseries_metadata: dict[str, Any]):
        errors = []
        for i, per_section_parameter in enumerate(tiltseries_metadata["per_section_parameter"]):
            phase_shift = per_section_parameter["phase_shift"]
            if phase_shift is None:
                continue
            try:
                assert 0 <= phase_shift <= 2 * np.pi
            except AssertionError:
                errors.append(f"per_section_parameter[{i}].phase_shift= {phase_shift} is out of range [0, 2*pi].")
        if len(errors) > 0:
            raise AssertionError("\n".join(errors))

    @allure.title("PerSectionParameters: maxResolution > 0 (>= 0 for IMOD format).")
    def test_max_resolution(self, tiltseries_metadata: dict[str, Any]):
        is_imod = tiltseries_metadata.get("format") == "IMOD"
        errors = []
        for i, per_section_parameter in enumerate(tiltseries_metadata["per_section_parameter"]):
            max_resolution = per_section_parameter["max_resolution"]
            if max_resolution is None:
                continue
            try:
                if is_imod:
                    assert max_resolution >= 0
                else:
                    assert max_resolution > 0
            except AssertionError:
                if is_imod:
                    errors.append(f"per_section_parameter[{i}].max_resolution= {max_resolution} is not greater than or equal to 0.")
                else:
                    errors.append(f"per_section_parameter[{i}].max_resolution= {max_resolution} is not greater than 0.")
        if len(errors) > 0:
            raise AssertionError("\n".join(errors))

    @allure.title("PerSectionParameters: All raw tilt angles match to a mdoc TiltAngle (+-10^-2 deg).")
    def test_raw_angle(self, tiltseries_metadata: dict[str, Any], mdoc_data: pd.DataFrame):
        errors = helper_angles_injection_errors(
            [psp["raw_angle"] for psp in tiltseries_metadata["per_section_parameter"]],
            mdoc_data["TiltAngle"].to_list(),
            "tiltseries metadata per_section_parameter raw_angle",
            "mdoc file",
            angle_tolerance=10 ** -2,
        )
        if errors:
            raise AssertionError("\n".join(errors))

    @allure.title("PerSectionParameters: 0 <= zIndex <= (z-Dimension of tilt series - 1).")
    def test_z_index(self, tiltseries_metadata: dict[str, Any]):
        errors = []
        for i, per_section_parameter in enumerate(tiltseries_metadata["per_section_parameter"]):
            z_index = per_section_parameter["z_index"]
            try:
                assert 0 <= z_index <= (tiltseries_metadata["size"]["z"] - 1)
            except AssertionError:
                errors.append(f"per_section_parameter[{i}].z_index= {z_index} is out of range [0, {tiltseries_metadata['size']['z'] - 1}].")
        if len(errors) > 0:
            raise AssertionError("\n".join(errors))
