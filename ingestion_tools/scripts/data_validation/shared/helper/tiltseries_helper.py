import re
from typing import Any

import allure
import numpy as np
import pandas as pd
import pytest
from data_validation.shared.helper.helper_mrc_zarr import HelperTestMRCZarrHeader

TILT_AXIS_ANGLE_REGEX = re.compile(r".*tilt\s*axis\s*angle\s*=\s*([-+]?(?:\d*\.*\d+))")


class TiltSeriesHelper(HelperTestMRCZarrHeader):

    @pytest.fixture(autouse=True)
    def set_space_group(self):
        self.spacegroup = 0  # 2D image

    @pytest.fixture
    def tiltseries_metadata_range(self, tiltseries_metadata: dict) -> list[float]:
        # add tilt_step to max because arange is end value exclusive
        return np.arange(
            tiltseries_metadata["tilt_range"]["min"],
            tiltseries_metadata["tilt_range"]["max"] + tiltseries_metadata["tilt_step"],
            tiltseries_metadata["tilt_step"],
        ).tolist()

    @pytest.fixture
    def mdoc_tilt_axis_angle(self, mdoc_data: pd.DataFrame) -> float:
        # To convert the data from the mdoc into a data frame, all the global records are added to each section's data
        titles = mdoc_data["titles"][0]
        for title in titles:
            if result := re.match(TILT_AXIS_ANGLE_REGEX, title.lower()):
                return float(result[1])
        pytest.fail("No Tilt axis angle found")

    @allure.title("Tiltseries: tilt axis angle is consistent with mdoc file.")
    def test_tilt_axis_angle(self, mdoc_tilt_axis_angle: float, tiltseries_metadata: dict):
        metadata_tilt_axis = tiltseries_metadata.get("tilt_axis")
        assert (
            metadata_tilt_axis - 10 <= mdoc_tilt_axis_angle <= metadata_tilt_axis + 10
        ), f"Tilt axis angle mismatch: MDOC: {mdoc_tilt_axis_angle} vs Metadata: {metadata_tilt_axis}"

    @allure.title("PerSectionParameters: number of frames >= # of per section parameters.")
    def test_persion_section_parameter_with_num_frames(self, tiltseries_metadata: dict[str, Any], frame_metadata: dict[str, dict]):
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
        assert len(errors) == 0, "\n".join(errors)

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
        assert len(errors) == 0, "\n".join(errors)

    @allure.title("PerSectionParameters: maxResolution > 0.")
    def test_max_resolution(self, tiltseries_metadata: dict[str, Any]):
        errors = []
        for i, per_section_parameter in enumerate(tiltseries_metadata["per_section_parameter"]):
            max_resolution = per_section_parameter["max_resolution"]
            if max_resolution is None:
                continue
            try:
                assert max_resolution > 0
            except AssertionError:
                errors.append(f"per_section_parameter[{i}].max_resolution= {max_resolution} is not greater than 0.")
        assert len(errors) == 0, "\n".join(errors)

    @allure.title("PerSectionParameters: rawAngle matches mdoc angle.")
    def test_raw_angle(self, tiltseries_metadata: dict[str, Any], mdoc_tilt_axis_angle: float):
        errors = []
        for i, per_section_parameter in enumerate(tiltseries_metadata["per_section_parameter"]):
            raw_angle = per_section_parameter["raw_angle"]
            try:
                assert raw_angle == mdoc_tilt_axis_angle
            except AssertionError:
                errors.append(f"per_section_parameter[{i}].raw_angle= {raw_angle} does not match mdoc angle {mdoc_tilt_axis_angle}.")
        assert len(errors) == 0, "\n".join(errors)

    @allure.title("PerSectionParameters: 0 <= zIndex <= (z-Dimension of tilt series - 1).")
    def test_z_index(self, tiltseries_metadata: dict[str, Any]):
        errors = []
        for i, per_section_parameter in enumerate(tiltseries_metadata["per_section_parameter"]):
            z_index = per_section_parameter["z_index"]
            try:
                assert 0 <= z_index <= (tiltseries_metadata["size"]["z"] - 1)
            except AssertionError:
                errors.append(f"per_section_parameter[{i}].z_index= {z_index} is out of range [0, {tiltseries_metadata['size']['z'] - 1}].")
        assert len(errors) == 0, "\n".join(errors)
