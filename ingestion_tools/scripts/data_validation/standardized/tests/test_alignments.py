from typing import Dict, List

import allure
import numpy as np
import pandas as pd
import pytest
from data_validation.shared.helper.angles_helper import helper_angles_injection_errors


@pytest.mark.alignment
@pytest.mark.parametrize("dataset, run_name, aln_dir", pytest.cryoet.dataset_run_alignment_combinations, scope="session")
class TestAlignments:
    """
    A class to test alignment tilt angle data. Only checking that the # of angles in these files are consistent with other files /
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

    @pytest.fixture
    def alignment_tiltseries_metadata_range(self, alignment_tiltseries_metadata: Dict) -> List[float]:
        # add tilt_step to max because arange is end value exclusive
        return np.arange(
            alignment_tiltseries_metadata["tilt_range"]["min"],
            alignment_tiltseries_metadata["tilt_range"]["max"] + alignment_tiltseries_metadata["tilt_step"],
            alignment_tiltseries_metadata["tilt_step"],
        ).tolist()

    ### BEGIN Tilt .tlt tests ###
    @allure.title("Alignment: angles exist.")
    def test_tilt_count(self, alignment_tilt: pd.DataFrame):
        assert len(alignment_tilt) > 0

    @allure.title("Alignment: angles are within the expected range [-90, 90].")
    def test_tilt_angle_range(self, alignment_tilt: pd.DataFrame):
        assert all(-90 <= angle <= 90 for angle in alignment_tilt["TiltAngle"])

    @allure.title("Alignment: every tilt angle maps to a raw tilt angle.")
    def test_tilt_raw_tilt(self, alignment_tilt: pd.DataFrame, alignment_tiltseries_raw_tilt: pd.DataFrame):
        errors = helper_angles_injection_errors(
            alignment_tilt["TiltAngle"].to_list(),
            alignment_tiltseries_raw_tilt["TiltAngle"].to_list(),
            "tilt file",
            "raw tilt file",
        )
        if len(errors) > 0:
            raise AssertionError("\n".join(errors))

    @allure.title("Alignment: every tilt angle maps to a mdoc tilt angle.")
    def test_tilt_mdoc(self, alignment_tilt: pd.DataFrame, mdoc_data: pd.DataFrame):
        errors = helper_angles_injection_errors(
            alignment_tilt["TiltAngle"].to_list(),
            mdoc_data["TiltAngle"].to_list(),
            "tilt file",
            "mdoc file",
        )
        if len(errors) > 0:
            raise AssertionError("\n".join(errors))

    @allure.title(
        "Raw tilt: number of raw tilt angles are must be equal to tiltseries size['z'] (implied to be the number of frames files).",
    )
    def test_tilt_tiltseries_metadata(self, alignment_tilt: pd.DataFrame, alignment_tiltseries_metadata: Dict):
        assert len(alignment_tilt) <= alignment_tiltseries_metadata["size"]["z"]

    @allure.title("Alignment: angles correspond to the tilt_range + tilt_step metadata field.")
    @allure.description("Not all angles in the tilt range must be present in the tilt file.")
    def test_tilt_tiltseries_range(
        self,
        alignment_tilt: pd.DataFrame,
        alignment_tiltseries_metadata: Dict,
        alignment_tiltseries_metadata_range: List[float],
    ):
        errors = helper_angles_injection_errors(
            alignment_tilt["TiltAngle"].to_list(),
            alignment_tiltseries_metadata_range,
            "tilt file",
            "tiltseries metadata tilt_range",
        )
        assert len(errors) == 0, (
            "\n".join(errors)
            + f"\nRange: {alignment_tiltseries_metadata['tilt_range']['min']} to {alignment_tiltseries_metadata['tilt_range']['max']}, with step {alignment_tiltseries_metadata['tilt_step']}"
        )

    @allure.title("Alignment: tilt axis angle in mdoc file matches that in the alignment metadata [per_section_alignment_parameters.in_plane_rotation] (+/- 10 deg)")
    def test_mdoc_tilt_axis_angle_in_alignment_per_section_alignment_parameters(self, mdoc_data: pd.DataFrame, alignment_tiltseries_metadata: dict[str, dict]):
        per_section_alignment_parameters = alignment_tiltseries_metadata.get("per_section_alignment_parameters")
        if not per_section_alignment_parameters:
            pytest.skip("Alignment metadata missing per_section_alignment_parameters.")
        errors = []
        for i, psap in enumerate(per_section_alignment_parameters):
            if in_plane_rotation:=psap.get("in_plane_rotation") is not None:
                try:
                    assert abs(mdoc_data["TiltAxisAngle"].iloc[0] - in_plane_rotation) < 10, \
                        f"Tilt axis angle in mdoc file {mdoc_data['TiltAxisAngle'].iloc[0]} does not match alignment metadata['per_section_alignment_parameter'][{i}]['tilt_angle']: {in_plane_rotation}"
                except AssertionError as e:
                    errors.append(str(e))
        assert not errors, "\n".join(errors)

    ### END Tiltseries consistency tests ###
