import allure
import pandas as pd
from data_validation.shared.helper.angles_helper import helper_angles_injection_errors


class TiltAnglesHelper:
    """
    A helper class to test tilt angle data. Only checking that the # of angles in these files are consistent with
    other files / data and that they properly map to other files / data. Other data validation tests is done in
    respective classes.
    Spans .tlt, .rawtlt, .mdoc, frames files.
    Ordering:
        - .tlt (<=) maps to .rawtlt (not necessarily 1:1)
        - .rawtlt (<=) maps to .mdoc (not necessarily 1:1)

    Extra test redundancy is added for the cases where files sometimes do not exist.
    """

    ### BEGIN Raw Tilt .rawtlt tests ###
    @allure.title("Raw tilt: angles exist.")
    def test_raw_tilt_count(self, raw_tilt_data: pd.DataFrame):
        assert len(raw_tilt_data) > 0, "No tilt angles found in raw tilt file."

    @allure.title("Raw tilt: angles are within the expected range [-90, 90].")
    def test_raw_tilt_angle_range(self, raw_tilt_data: pd.DataFrame):
        assert all(-90 <= angle <= 90 for angle in raw_tilt_data["TiltAngle"]), "Tilt angles are not within [-90, 90]"

    @allure.title("Raw tilt: # raw tilt angle not greater than # mdoc sections")
    def test_raw_tilt_mdoc_entries(self, raw_tilt_data: pd.DataFrame, mdoc_data: pd.DataFrame):
        assert len(mdoc_data) >= len(raw_tilt_data), "More raw tilt angles than mdoc sections"

    @allure.title("Raw tilt: every raw tilt angle matches a mdoc tilt angle.")
    def test_raw_tilt_mdoc(self, raw_tilt_data: pd.DataFrame, mdoc_data: pd.DataFrame):
        errors = helper_angles_injection_errors(
            raw_tilt_data["TiltAngle"].to_list(),
            mdoc_data["TiltAngle"].to_list(),
            "raw tilt file",
            "mdoc file",
        )
        if len(errors) > 0:
            raise AssertionError("\n".join(errors))
