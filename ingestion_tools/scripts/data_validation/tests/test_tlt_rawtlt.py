from typing import List

import pandas as pd
import pytest
from tests.helper_functions import helper_angles_injection_errors

ANGLE_TOLERANCE = 0.01


@pytest.mark.tilt
@pytest.mark.metadata
@pytest.mark.parametrize("run_name", pytest.run_name, scope="session")
class TestTiltAndRawTilt:
    ### BEGIN Tilt .tlt tests ###
    def test_tilt_count(self, tiltseries_tilt: pd.DataFrame):
        """Ensure that there are tilt angles."""
        assert len(tiltseries_tilt) > 0

    def test_tilt_angle_range(self, tiltseries_tilt: pd.DataFrame):
        """Ensure that the tilt angles are within the expected range."""
        assert all(-90 <= angle <= 90 for angle in tiltseries_tilt["TiltAngle"])

    def test_tilt_raw_tilt(self, tiltseries_tilt: pd.DataFrame, tiltseries_raw_tilt: pd.DataFrame):
        """Ensure that every tilt angle matches to a raw tilt angle."""
        errors = self.helper_angles_injection_errors(
            tiltseries_tilt["TiltAngle"].to_list(),
            tiltseries_raw_tilt["TiltAngle"].to_list(),
            "tilt file",
            "raw tilt file",
        )
        assert len(errors) == 0, "\n".join(errors)

    def test_tilt_frames(self, tiltseries_tilt: pd.DataFrame, frames_files: List[str]):
        """Ensure that there are at least the same number of frame files as tilt angles."""
        assert len(frames_files) >= len(tiltseries_tilt)

    ### BEGIN Raw Tilt .rawtlt tests ###
    def test_raw_tilt_count(self, tiltseries_raw_tilt: pd.DataFrame):
        """Ensure that there are raw tilt angles."""
        assert len(tiltseries_raw_tilt) > 0

    def test_raw_tilt_angle_range(self, tiltseries_raw_tilt: pd.DataFrame):
        """Ensure that the raw tilt angles are within the expected range."""
        assert all(-90 <= angle <= 90 for angle in tiltseries_raw_tilt["TiltAngle"])

    def test_raw_tilt_tiltseries_mdoc(self, tiltseries_raw_tilt: pd.DataFrame, tiltseries_mdoc: pd.DataFrame):
        """Ensure that every raw tilt angle matches a tilt angle in the mdoc file."""
        errors = helper_angles_injection_errors(
            tiltseries_raw_tilt["TiltAngle"].to_list(),
            tiltseries_mdoc["TiltAngle"].to_list(),
            "raw tilt file",
            "mdoc file",
        )
        assert len(errors) == 0, "\n".join(errors)

    # def test_raw_tilt_tiltseries_mdoc_one_to_one(
    #     self,
    #     tiltseries_raw_tilt: pd.DataFrame,
    #     tiltseries_mdoc: pd.DataFrame,
    # ):
    #     """Ensure that every raw tilt angle matches a tilt angle in the mdoc file and vice versa."""
    #     errors = helper_angles_one_to_one_errors(
    #         tiltseries_raw_tilt["TiltAngle"].to_list(),
    #         tiltseries_mdoc["TiltAngle"].to_list(),
    #         "raw tilt file",
    #         "mdoc file",
    #     )
    #     assert len(errors) == 0, "\n".join(errors)

    def test_raw_tilt_frames(self, tiltseries_raw_tilt: pd.DataFrame, frames_files: List[str]):
        """Ensure that there are at least the same number of frame files as raw tilt angles."""
        assert len(frames_files) >= len(tiltseries_raw_tilt)
