import re
import warnings
from typing import Dict, List

import numpy as np
import pandas as pd
import pytest

# TODO: Should this be a check? Am I missing any extensions?
PERMITTED_FRAME_EXTENSIONS = [".mrc", ".tif", ".tiff", ".eer", ".bz2"]


@pytest.mark.frame
@pytest.mark.metadata
@pytest.mark.parametrize("run_name", pytest.run_name, scope="session")
class TestFrame:
    ### BEGIN Self-consistency tests ###

    def test_frames_format(self, frame_files: List[str]):
        errors = []

        for frame_file in frame_files:
            if not any(frame_file.endswith(ext) for ext in PERMITTED_FRAME_EXTENSIONS):
                errors.append(f"Invalid frame file extension: {frame_file}")

        assert not errors, "\n".join(errors)

    ### END Self-consistency tests ###

    ### BEGIN Tiltseries consistency tests ###
    def test_frames_count(self, frame_files: List[str], tiltseries_metadata: Dict):
        """Check that the number of frames is consistent between the metadata and the frame files."""
        assert len(frame_files) == tiltseries_metadata["frames_count"]

    def check_angles(
        self,
        angles: np.ndarray,
        frames_dir: str,
        frame_files: List[str],
        # tiltseries_metadata: Dict,
    ):
        tilt_angle_to_frame_mapping = {}
        remaining_frame_files = frame_files.copy()

        # TODO: Figure out how to handle bidirectional case with double 0 tilt angle sample
        # bidirectional = "bidirectional" in tiltseries_metadata["tilting_scheme"].lower() or "bi-directional" in tiltseries_metadata["tilting_scheme"].lower()

        for angle in angles:
            # Look for a frame file that contains the tilt angle
            angle_regex = re.compile(f"{frames_dir}.*_{'{:.1f}'.format(angle).replace('.', r'\.')}_.*")
            angle_files = list(filter(angle_regex.match, remaining_frame_files))
            assert len(angle_files) <= 1
            if len(angle_files) == 0:
                warnings.warn(f"Warning: Missing frame file for tilt angle {angle}", stacklevel=2)
                continue
            remaining_frame_files.remove(angle_files[0])
            tilt_angle_to_frame_mapping[angle] = angle_files[0]

        assert len(remaining_frame_files) == 0

    def test_frames_filenames(self, frames_dir: str, frame_files: List[str], tiltseries_metadata: Dict):
        """Check that the filenames of the frames are consistent with the metadata."""

        angles = np.arange(
            tiltseries_metadata["tilt_range"]["min"],
            tiltseries_metadata["tilt_range"]["max"] + tiltseries_metadata["tilt_step"],
            tiltseries_metadata["tilt_step"],
        )
        self.check_angles(angles, frames_dir, frame_files)

    def test_frames_mdoc(
        self,
        frames_dir: str,
        frame_files: List[str],
        tiltseries_mdoc: pd.DataFrame,
        tiltseries_metadata: Dict,
    ):
        """Check that the tiltseries mdoc file contains the expected number of frames and that all listed frames exist."""
        assert len(tiltseries_mdoc) == tiltseries_metadata["frames_count"]

        # TODO: Figure out some way to check against tiltseries_mdoc["SubFramePath"], which currently does not point to the s3 files but to the original file paths
        self.check_angles(tiltseries_mdoc["TiltAngle"], frames_dir, frame_files)

    ### END Tiltseries consistency tests ###
