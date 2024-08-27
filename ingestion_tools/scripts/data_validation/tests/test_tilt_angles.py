import os
from typing import Dict, List

import numpy as np
import pandas as pd
import pytest
from tests.helper_functions import helper_angles_injection_errors


@pytest.mark.tilt_angles
@pytest.mark.metadata
@pytest.mark.parametrize("run_name", pytest.run_name, scope="session")
class TestTiltAngles:
    """
    A class to test tilt angle data (only ordering, other data validation tests are done in respective classes).
    Spans .tlt, .rawtlt, .mdoc, tiltseries_metadata.json, frames files.
    Ordering:
        - .tlt (<=) maps to .rawtlt (not necessarily 1:1)
        - .rawtlt (<=) maps to .mdoc (not necessarily 1:1)
        - .mdoc (<=) maps to tiltseries_metadata.json "frames_count" (not necessarily 1:1)
        - tiltseries metadata size["z"] == frames_count == # of frames files
        - # of frames_files <= metadata tilt_range (see max_frames_count fixture)

    Extra test redundancy is added for the cases where files sometimes do not exist.
    Extra redundancy tests are done on the tiltseries metadata size["z"] since frames_count / # of frames files may be 0
        when no frames are present and that is a valid case. To ensure consistency, we rely on the check
        tiltseries metadata size["z"] == frames_count == # of frames files.
    """

    @pytest.fixture(autouse=True)
    def max_frames_count(self, tiltseries_metadata: Dict):
        # TODO FIXME how to check if -0.0 should exist
        return (
            tiltseries_metadata["tilt_range"]["max"] - tiltseries_metadata["tilt_range"]["min"]
        ) / tiltseries_metadata["tilt_step"] + 1

    ### BEGIN Tilt .tlt tests ###
    def test_tilt_count(self, tiltseries_tilt: pd.DataFrame):
        """Ensure that there are tilt angles."""
        assert len(tiltseries_tilt) > 0

    def test_tilt_angle_range(self, tiltseries_tilt: pd.DataFrame):
        """Ensure that the tilt angles are within the expected range."""
        assert all(-90 <= angle <= 90 for angle in tiltseries_tilt["TiltAngle"])

    def test_tilt_raw_tilt(self, tiltseries_tilt: pd.DataFrame, tiltseries_raw_tilt: pd.DataFrame):
        """Ensure that every tilt angle matches to a raw tilt angle."""
        errors = helper_angles_injection_errors(
            tiltseries_tilt["TiltAngle"].to_list(),
            tiltseries_raw_tilt["TiltAngle"].to_list(),
            "tilt file",
            "raw tilt file",
        )
        assert len(errors) == 0, "\n".join(errors)

    def test_tilt_mdoc(self, tiltseries_tilt: pd.DataFrame, tiltseries_mdoc: pd.DataFrame):
        """Ensure that every tilt angle matches to a mdoc tilt angle."""
        errors = helper_angles_injection_errors(
            tiltseries_tilt["TiltAngle"].to_list(),
            tiltseries_mdoc["TiltAngle"].to_list(),
            "tilt file",
            "mdoc file",
        )
        assert len(errors) == 0, "\n".join(errors)

    def test_tilt_frames(self, tiltseries_tilt: pd.DataFrame, frames_files: List[str]):
        """Ensure that there are at least the same number of frame files as tilt angles."""
        assert len(tiltseries_tilt) <= len(frames_files)

    def test_tilt_max_frames_count(self, tiltseries_tilt: pd.DataFrame, max_frames_count: int):
        """Ensure that the tilt angles are consistent with the max frames count."""
        assert len(tiltseries_tilt) <= max_frames_count

    ### BEGIN Raw Tilt .rawtlt tests ###
    def test_raw_tilt_count(self, tiltseries_raw_tilt: pd.DataFrame):
        """Ensure that there are raw tilt angles."""
        assert len(tiltseries_raw_tilt) > 0

    def test_raw_tilt_angle_range(self, tiltseries_raw_tilt: pd.DataFrame):
        """Ensure that the raw tilt angles are within the expected range."""
        assert all(-90 <= angle <= 90 for angle in tiltseries_raw_tilt["TiltAngle"])

    def test_raw_tilt_mdoc(self, tiltseries_raw_tilt: pd.DataFrame, tiltseries_mdoc: pd.DataFrame):
        """Ensure that every raw tilt angle matches a tilt angle in the mdoc file."""
        errors = helper_angles_injection_errors(
            tiltseries_raw_tilt["TiltAngle"].to_list(),
            tiltseries_mdoc["TiltAngle"].to_list(),
            "raw tilt file",
            "mdoc file",
        )
        assert len(errors) == 0, "\n".join(errors)

    def test_raw_tilt_frames(self, tiltseries_raw_tilt: pd.DataFrame, frames_files: List[str]):
        """Ensure that there are at least the same number of frame files as raw tilt angles."""
        assert len(tiltseries_raw_tilt) <= len(frames_files)

    def test_raw_tilt_max_frames_count(self, tiltseries_raw_tilt: pd.DataFrame, max_frames_count: int):
        """Ensure that the raw tilt angles are consistent with the max frames count."""
        assert len(tiltseries_raw_tilt) <= max_frames_count

    ### BEGIN MDOC tests ###
    def test_tiltseries_mdoc_range(self, tiltseries_mdoc: pd.DataFrame):
        """Check that the tiltseries mdoc angles are within the range specified in the metadata."""
        assert tiltseries_mdoc["TiltAngle"].min() >= -90
        assert tiltseries_mdoc["TiltAngle"].max() <= 90

    def test_mdoc_frames(self, tiltseries_mdoc: pd.DataFrame, frames_files: List[str]):
        """Ensure that there are at least the same number of frame files as mdoc tilt angles."""
        assert len(tiltseries_mdoc) <= len(frames_files)

    def test_mdoc_max_frames_count(self, tiltseries_mdoc: pd.DataFrame, max_frames_count: int):
        """Ensure that the mdoc tilt angles are consistent with the max frames count."""
        assert len(tiltseries_mdoc) <= max_frames_count

    def test_mdoc_frame_paths_exist(
        self,
        frames_files: List[str],
        tiltseries_mdoc: pd.DataFrame,
    ):
        """Check that all mdoc frame entries exist (however not all frames files have to be listed in mdoc)."""
        missing_frames = []
        remaining_frames_files_basenames = [os.path.basename(f) for f in frames_files]
        for _, row in tiltseries_mdoc.iterrows():
            frame_file = os.path.basename(str(row["SubFramePath"]).replace("\\", "/"))
            if frame_file not in remaining_frames_files_basenames:
                missing_frames.append(frame_file)
            else:
                remaining_frames_files_basenames.remove(frame_file)

        assert not missing_frames, f"Missing frames: {missing_frames}"

    def test_tiltseries_tilt_range_mdoc(self, tiltseries_metadata: Dict, tiltseries_mdoc: pd.DataFrame):
        """
        Check that the tiltseries mdoc angles correspond to the tilt_range + tilt_step metadata field.
        Not all angles in the tilt range must be present in the MDOC file.
        """
        errors = helper_angles_injection_errors(
            tiltseries_mdoc["TiltAngle"].to_list(),
            np.arange(
                tiltseries_metadata["tilt_range"]["min"],
                tiltseries_metadata["tilt_range"]["max"],
                tiltseries_metadata["tilt_step"],
            ).tolist(),
            "mdoc file",
            "tiltseries metadata tilt_range",
        )
        assert len(errors) == 0, (
            "\n".join(errors)
            + f"\nRange: {tiltseries_metadata['tilt_range']['min']} to {tiltseries_metadata['tilt_range']['max']}, with step {tiltseries_metadata['tilt_step']}"
        )

    ### BEGIN frames files tests ###
    def test_frames_count(self, frames_files: List[str], tiltseries_metadata: Dict, max_frames_count: int):
        """
        Ensure that the number of frames files is consistent with the frames_count metadata field.
        """
        assert len(frames_files) == tiltseries_metadata["frames_count"]
        assert len(frames_files) == tiltseries_metadata["size"]["z"]
        assert len(frames_files) <= max_frames_count
