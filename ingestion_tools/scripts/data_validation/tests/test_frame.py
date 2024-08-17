import re
import warnings
from typing import Dict, List, Union

import numpy as np
import pandas as pd
import pytest
import tifffile
from helper_mrc import HelperTestMRCHeader
from mrcfile.mrcinterpreter import MrcInterpreter

# TODO: Should this be a check? Am I missing any extensions?
PERMITTED_FRAME_EXTENSIONS = [".mrc", ".tif", ".tiff", ".eer", ".bz2"]
MAX_FRAME_SIZE = 250 * 1024 * 1024  # 250 MB


@pytest.mark.frame
@pytest.mark.metadata
@pytest.mark.parametrize("run_name", pytest.run_name, scope="session")
class TestFrame(HelperTestMRCHeader):
    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_header_class_variables(
        self,
        frames_headers: Dict[str, Union[tifffile.TiffPages, MrcInterpreter]],
    ):
        self.spacegroup = 0  # 2D image
        self.mrc_headers = {k: v for k, v in frames_headers.items() if isinstance(v, MrcInterpreter)}

    ### BEGIN Self-consistency tests ###
    def test_frames_format(self, frames_files: List[str]):
        errors = []

        for frame_file in frames_files:
            if not any(frame_file.endswith(ext) for ext in PERMITTED_FRAME_EXTENSIONS):
                errors.append(f"Invalid frame file extension: {frame_file}")

        assert not errors, "\n".join(errors)

    def test_frames_dimensions(self, frames_headers: Dict[str, Union[tifffile.TiffPages, MrcInterpreter]]):
        """Check that the frame dimensions are consistent."""
        errors = []
        frames_dimensions = None

        for _, header in frames_headers.items():
            if isinstance(header, tifffile.TiffPages):
                curr_dimensions = header[0].shape
                # first ensure all pages have the same dimensions
                # this loop takes a long time, need to multithread
                assert all(page.shape == curr_dimensions for page in header), "Not all pages have the same dimensions"
                if frames_dimensions is None:
                    frames_dimensions = curr_dimensions
                elif curr_dimensions != frames_dimensions:
                    errors.append(f"Frame dimensions do not match: {curr_dimensions} != {frames_dimensions}")
            elif isinstance(header, MrcInterpreter):
                if frames_dimensions is None:
                    frames_dimensions = (header.nx, header.ny)
                elif (header.nx, header.ny) != frames_dimensions:
                    errors.append(f"Frame dimensions do not match: ({header.nx}, {header.ny}) != {frames_dimensions}")

        assert not errors, "\n".join(errors)

    ### END Self-consistency tests ###

    ### BEGIN Tiltseries consistency tests ###
    def test_frames_count(self, frames_files: List[str], tiltseries_metadata: Dict):
        """Check that the number of frames is consistent between the metadata and the frame files."""
        assert len(frames_files) == tiltseries_metadata["frames_count"]

    def check_angles(
        self,
        angles: np.ndarray,
        frames_dir: str,
        frames_files: List[str],
        # tiltseries_metadata: Dict,
    ):
        tilt_angle_to_frame_mapping: Dict[Union[str, float], str] = {}  # only str key for -0.0
        remaining_frames_files = frames_files.copy()

        for angle in angles:
            # Look for a frame file that contains the tilt angle
            angle_str = "({:.1f}|{:.2f})".format(angle, angle).replace(".", r"\.")
            angle_regex = re.compile(f"{frames_dir}.*_{angle_str}.*")
            angle_files = list(filter(angle_regex.match, remaining_frames_files))
            assert len(angle_files) <= 1
            if len(angle_files) == 0:
                warnings.warn(f"Missing frame file for tilt angle {angle}", stacklevel=2)
                continue
            remaining_frames_files.remove(angle_files[0])
            if angle in tilt_angle_to_frame_mapping:
                warnings.warn(f"Duplicate / ambiguous frame file for tilt angle {angle}", stacklevel=2)
            tilt_angle_to_frame_mapping[angle] = angle_files[0]

        # special case for -0.0
        angle_str = "(-0.0|-0.00)"
        angle_regex = re.compile(f"{frames_dir}.*_{angle_str}.*")
        angle_files = list(filter(angle_regex.match, remaining_frames_files))
        assert len(angle_files) <= 1
        if len(angle_files) == 1:
            remaining_frames_files.remove(angle_files[0])
            # usually key is float, but -0.0 is a special case
            tilt_angle_to_frame_mapping["-0.0"] = angle_files[0]

        assert remaining_frames_files == [], f"Frame files not accounted for: {remaining_frames_files}"

    def test_frames_filenames(self, frames_dir: str, frames_files: List[str], tiltseries_metadata: Dict):
        """Check that the filenames of the frames are consistent with the metadata."""

        angles = np.arange(
            tiltseries_metadata["tilt_range"]["min"],
            tiltseries_metadata["tilt_range"]["max"] + tiltseries_metadata["tilt_step"],
            tiltseries_metadata["tilt_step"],
        )
        self.check_angles(angles, frames_dir, frames_files)

    def test_frames_mdoc(
        self,
        frames_dir: str,
        frames_files: List[str],
        tiltseries_mdoc: pd.DataFrame,
        tiltseries_metadata: Dict,
    ):
        """Check that the tiltseries mdoc file contains the expected number of frames and that all listed frames exist."""
        assert len(tiltseries_mdoc) == tiltseries_metadata["frames_count"]

        # TODO: Figure out some way to check against tiltseries_mdoc["SubFramePath"], which currently does not point to the s3 files but to the original file paths
        self.check_angles(tiltseries_mdoc["TiltAngle"], frames_dir, frames_files)

    ### END Tiltseries consistency tests ###
