from typing import Dict, List, Union

import allure
import numpy as np
import pandas as pd
import pytest
import tifffile
from helper_angles import helper_angles_injection_errors
from mrcfile.mrcinterpreter import MrcInterpreter

ANGLE_TOLERANCE = 0.05


@pytest.mark.tilt_angles
@pytest.mark.parametrize("dataset, run_name, ts_dir", pytest.dataset_run_tiltseries_combinations, scope="session")
class TestTiltAngles:
    """
    A class to test tilt angle data. Only checking that the # of angles in these files are consistent with other files /
    data and that they properly map to other files / data. Other data validation tests is done in respective classes.
    Spans .tlt, .rawtlt, .mdoc, tiltseries_metadata.json, frames files.
    Ordering:
        - .tlt (<=) maps to .rawtlt (not necessarily 1:1)
        - .rawtlt (<=) maps to .mdoc (not necessarily 1:1)
        - .mdoc (==) one-to-one with frames files & tiltseries_metadata size["z"]
        - tiltseries metadata size["z"] == frames_count == # of frames files

    Extra test redundancy is added for the cases where files sometimes do not exist.
    Extra redundancy tests are done on the tiltseries metadata size["z"] since frames_count / # of frames files may be 0
        when no frames are present and that is a valid case. To ensure consistency, we rely on the check
        tiltseries metadata size["z"] == frames_count == # of frames files.
    """

    ### BEGIN Fixtures ###
    @pytest.fixture
    def tiltseries_metadata_range(self, tiltseries_metadata: Dict) -> List[float]:
        # add tilt_step to max because arange is end value exclusive
        return np.arange(
            tiltseries_metadata["tilt_range"]["min"],
            tiltseries_metadata["tilt_range"]["max"] + tiltseries_metadata["tilt_step"],
            tiltseries_metadata["tilt_step"],
        ).tolist()


    ### BEGIN Raw Tilt .rawtlt tests ###
    @allure.title("Raw tilt: angles exist.")
    def test_raw_tilt_count(self, tiltseries_raw_tilt: pd.DataFrame):
        assert len(tiltseries_raw_tilt) > 0

    @allure.title("Raw tilt: angles are within the expected range [-90, 90].")
    def test_raw_tilt_angle_range(self, tiltseries_raw_tilt: pd.DataFrame):
        assert all(-90 <= angle <= 90 for angle in tiltseries_raw_tilt["TiltAngle"])

    @allure.title("Raw tilt: every raw tilt angle matches a mdoc tilt angle.")
    def test_raw_tilt_mdoc(self, tiltseries_raw_tilt: pd.DataFrame, frames_mdoc: pd.DataFrame):
        errors = helper_angles_injection_errors(
            tiltseries_raw_tilt["TiltAngle"].to_list(),
            frames_mdoc["TiltAngle"].to_list(),
            "raw tilt file",
            "mdoc file",
        )
        assert len(errors) == 0, "\n".join(errors)

    @allure.title(
        "Raw tilt: number of raw tilt angles are less than or equal to tiltseries size['z'] (implied to be the number of frames files).",
    )
    def test_raw_tilt_tiltseries_metadata(self, tiltseries_raw_tilt: pd.DataFrame, tiltseries_metadata: Dict):
        assert len(tiltseries_raw_tilt) <= tiltseries_metadata["size"]["z"]

    ### BEGIN MDOC tests ###

    @allure.title("Mdoc: number of mdoc tilt angles equals tiltseries size['z'].")
    def test_mdoc_tiltseries_metadata(self, tiltseries_metadata: Dict, frames_mdoc: pd.DataFrame):
        assert len(frames_mdoc) == tiltseries_metadata["size"]["z"]

    @allure.title("Mdoc: every mdoc tilt angle corresponds to the tilt_range + tilt_step metadata field.")
    @allure.description("Not all angles in the tilt range must be present in the MDOC file.")
    def test_mdoc_tiltseries_range(
        self, tiltseries_metadata: Dict, frames_mdoc: pd.DataFrame, tiltseries_metadata_range: List[float],
    ):
        errors = helper_angles_injection_errors(
            frames_mdoc["TiltAngle"].to_list(),
            tiltseries_metadata_range,
            "mdoc file",
            "tiltseries metadata tilt_range",
        )
        assert len(errors) == 0, (
            "\n".join(errors)
            + f"\nRange: {tiltseries_metadata['tilt_range']['min']} to {tiltseries_metadata['tilt_range']['max']}, with step {tiltseries_metadata['tilt_step']}"
        )

    ### BEGIN Tiltseries consistency tests ###
    @allure.title("Frames: tiltseries pixel spacing is an integer multiple of the frame pixel spacing.")
    def test_tiltseries_pixel_spacing(
        self,
        dataset: str,
        frames_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]],
        tiltseries_metadata: Dict,
    ):
        for frame_file, frame_header in frames_headers.items():
            if isinstance(frame_header, MrcInterpreter):
                # only need to check the first frame, since we check that all frames have the same pixel spacing
                assert tiltseries_metadata["pixel_spacing"] / frame_header.voxel_size["x"] == pytest.approx(
                    round(tiltseries_metadata["pixel_spacing"] / frame_header.voxel_size["x"]),
                    abs=0.001,
                ), f"Pixel spacing does not match tiltseries metadata, {frame_file}"
                return

    ### END Tiltseries consistency tests ###
