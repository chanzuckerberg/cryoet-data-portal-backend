import os
from typing import Dict, List

import allure
import numpy as np
import pandas as pd
import pytest

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

    ### Helper functions ###
    # TODO FIXME account for double 0 sample
    def helper_angles_injection_errors(
        self,
        domain_angles: List[float],
        codomain_angles: List[float],
        domain_name: str,
        codomain_name: str,
    ) -> List[str]:
        """Helper function to check if all angles in the domain are in the codomain."""
        errors = []
        remaining_angles = codomain_angles.copy()
        for domain_angle in domain_angles:
            found_match = False
            for codomain_angle in codomain_angles:
                if abs(domain_angle - codomain_angle) < ANGLE_TOLERANCE:
                    found_match = True
                    remaining_angles.remove(codomain_angle)
                    break
            if not found_match:
                errors.append(
                    f"No match found: Looking for angle {domain_angle} (from {domain_name}) in {codomain_name}",
                )
        if len(domain_angles) > len(codomain_angles):
            errors.append(
                f"More angles in {domain_name} than in {codomain_name} ({len(domain_angles)} vs {len(codomain_angles)})",
            )
        return errors

    def helper_angles_bijection_errors(
        self,
        domain_angles: List[float],
        codomain_angles: List[float],
        domain_name: str,
        codomain_name: str,
    ) -> List[str]:
        """Helper function to check if all angles in the domain are in the codomain and vice versa."""
        injection_errors = self.helper_angles_injection_errors(
            domain_angles,
            codomain_angles,
            domain_name,
            codomain_name,
        )
        surjection_errors = self.helper_angles_injection_errors(
            codomain_angles,
            domain_angles,
            codomain_name,
            domain_name,
        )
        return injection_errors + surjection_errors

    ### BEGIN Tilt .tlt tests ###
    @allure.title("Tilt: angles exist.")
    def test_tilt_count(self, tiltseries_tilt: pd.DataFrame):
        assert len(tiltseries_tilt) > 0

    @allure.title("Tilt: angles are within the expected range [-90, 90].")
    def test_tilt_angle_range(self, tiltseries_tilt: pd.DataFrame):
        assert all(-90 <= angle <= 90 for angle in tiltseries_tilt["TiltAngle"])

    @allure.title("Tilt: every tilt angle maps to a raw tilt angle.")
    def test_tilt_raw_tilt(self, tiltseries_tilt: pd.DataFrame, tiltseries_raw_tilt: pd.DataFrame):
        errors = self.helper_angles_injection_errors(
            tiltseries_tilt["TiltAngle"].to_list(),
            tiltseries_raw_tilt["TiltAngle"].to_list(),
            "tilt file",
            "raw tilt file",
        )
        assert len(errors) == 0, "\n".join(errors)

    @allure.title("Tilt: every tilt angle maps to a mdoc tilt angle.")
    def test_tilt_mdoc(self, tiltseries_tilt: pd.DataFrame, tiltseries_mdoc: pd.DataFrame):
        errors = self.helper_angles_injection_errors(
            tiltseries_tilt["TiltAngle"].to_list(),
            tiltseries_mdoc["TiltAngle"].to_list(),
            "tilt file",
            "mdoc file",
        )
        assert len(errors) == 0, "\n".join(errors)

    @allure.title(
        "Raw tilt: number of raw tilt angles are less than or equal to tiltseries size['z'] (implied to be the number of frames files).",
    )
    def test_tilt_tiltseries_metadata(self, tiltseries_tilt: pd.DataFrame, tiltseries_metadata: Dict):
        assert len(tiltseries_tilt) <= tiltseries_metadata["size"]["z"]

    @allure.title("Tilt: angles correspond to the tilt_range + tilt_step metadata field.")
    @allure.description("Not all angles in the tilt range must be present in the tilt file.")
    def test_tilt_tiltseries_range(
        self, tiltseries_tilt: pd.DataFrame, tiltseries_metadata: Dict, tiltseries_metadata_range: List[float],
    ):
        errors = self.helper_angles_injection_errors(
            tiltseries_tilt["TiltAngle"].to_list(),
            tiltseries_metadata_range,
            "tilt file",
            "tiltseries metadata tilt_range",
        )
        assert len(errors) == 0, (
            "\n".join(errors)
            + f"\nRange: {tiltseries_metadata['tilt_range']['min']} to {tiltseries_metadata['tilt_range']['max']}, with step {tiltseries_metadata['tilt_step']}"
        )

    ### BEGIN Raw Tilt .rawtlt tests ###
    @allure.title("Raw tilt: angles exist.")
    def test_raw_tilt_count(self, tiltseries_raw_tilt: pd.DataFrame):
        assert len(tiltseries_raw_tilt) > 0

    @allure.title("Raw tilt: angles are within the expected range [-90, 90].")
    def test_raw_tilt_angle_range(self, tiltseries_raw_tilt: pd.DataFrame):
        assert all(-90 <= angle <= 90 for angle in tiltseries_raw_tilt["TiltAngle"])

    @allure.title("Raw tilt: every raw tilt angle matches a mdoc tilt angle.")
    def test_raw_tilt_mdoc(self, tiltseries_raw_tilt: pd.DataFrame, tiltseries_mdoc: pd.DataFrame):
        errors = self.helper_angles_injection_errors(
            tiltseries_raw_tilt["TiltAngle"].to_list(),
            tiltseries_mdoc["TiltAngle"].to_list(),
            "raw tilt file",
            "mdoc file",
        )
        assert len(errors) == 0, "\n".join(errors)

    @allure.title(
        "Raw tilt: number of raw tilt angles are less than or equal to tiltseries size['z'] (implied to be the number of frames files).",
    )
    def test_raw_tilt_tiltseries_metadata(self, tiltseries_raw_tilt: pd.DataFrame, tiltseries_metadata: Dict):
        assert len(tiltseries_raw_tilt) <= tiltseries_metadata["size"]["z"]

    @allure.title("Raw tilt: angles correspond to the tilt_range + tilt_step metadata field.")
    @allure.description("Not all angles in the tilt range must be present in the raw tilt file.")
    def test_raw_tilt_tiltseries_range(
        self, tiltseries_raw_tilt: pd.DataFrame, tiltseries_metadata: Dict, tiltseries_metadata_range: List[float],
    ):
        errors = self.helper_angles_injection_errors(
            tiltseries_raw_tilt["TiltAngle"].to_list(),
            tiltseries_metadata_range,
            "raw tilt file",
            "tiltseries metadata tilt_range",
        )
        assert len(errors) == 0, (
            "\n".join(errors)
            + f"\nRange: {tiltseries_metadata['tilt_range']['min']} to {tiltseries_metadata['tilt_range']['max']}, with step {tiltseries_metadata['tilt_step']}"
        )

    ### BEGIN MDOC tests ###
    @allure.title("Mdoc: tilt angles are within the expected range [-90, 90].")
    def test_tiltseries_mdoc_range(self, tiltseries_mdoc: pd.DataFrame):
        assert tiltseries_mdoc["TiltAngle"].min() >= -90
        assert tiltseries_mdoc["TiltAngle"].max() <= 90

    @allure.title("Mdoc: number of mdoc tilt angles equals number of frames files.")
    def test_mdoc_frames(self, tiltseries_mdoc: pd.DataFrame, frames_files: List[str]):
        assert len(tiltseries_mdoc) == len(frames_files)

    @allure.title("Mdoc: number of mdoc tilt angles equals tiltseries size['z'].")
    def test_mdoc_tiltseries_metadata(self, tiltseries_metadata: Dict, tiltseries_mdoc: pd.DataFrame):
        assert len(tiltseries_mdoc) == tiltseries_metadata["size"]["z"]

    @allure.title("Mdoc: Every mdoc tilt angle matches a frames file (one-to-one).")
    def test_mdoc_frame_paths(
        self,
        frames_files: List[str],
        tiltseries_mdoc: pd.DataFrame,
    ):
        standardize_frames_files = [os.path.basename(f) for f in frames_files]
        standardized_mdoc_entries = [
            os.path.basename(str(row["SubFramePath"]).replace("\\", "/")) for _, row in tiltseries_mdoc.iterrows()
        ]

        mdoc_with_missing_frames = [
            entry for entry in standardized_mdoc_entries if entry not in standardize_frames_files
        ]
        frames_with_missing_mdoc = [
            entry for entry in standardize_frames_files if entry not in standardized_mdoc_entries
        ]

        errors = []
        if len(standardize_frames_files) != len(standardized_mdoc_entries):
            errors.append(
                f"# of mdoc entries ({len(standardized_mdoc_entries)}) != # of frames files ({len(standardize_frames_files)})",
            )
        if mdoc_with_missing_frames:
            errors.append(f"mdoc entries do not have frames files: {mdoc_with_missing_frames}")
        if frames_with_missing_mdoc:
            errors.append(f"Frames files do not have mdoc entries: {frames_with_missing_mdoc}")

        assert len(errors) == 0, "\n".join(errors)

    @allure.title("Mdoc: every mdoc tilt angle corresponds to the tilt_range + tilt_step metadata field.")
    @allure.description("Not all angles in the tilt range must be present in the MDOC file.")
    def test_mdoc_tiltseries_range(
        self, tiltseries_metadata: Dict, tiltseries_mdoc: pd.DataFrame, tiltseries_metadata_range: List[float],
    ):
        errors = self.helper_angles_injection_errors(
            tiltseries_mdoc["TiltAngle"].to_list(),
            tiltseries_metadata_range,
            "mdoc file",
            "tiltseries metadata tilt_range",
        )
        assert len(errors) == 0, (
            "\n".join(errors)
            + f"\nRange: {tiltseries_metadata['tilt_range']['min']} to {tiltseries_metadata['tilt_range']['max']}, with step {tiltseries_metadata['tilt_step']}"
        )
