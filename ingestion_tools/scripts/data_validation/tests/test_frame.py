import os
from typing import Dict, List, Union

import pandas as pd
import pytest
import tifffile
from helper_mrc import HelperTestMRCHeader
from mrcfile.mrcinterpreter import MrcInterpreter

# TODO: Should this be a check? Am I missing any extensions?
PERMITTED_FRAME_EXTENSIONS = [".mrc", ".tif", ".tiff", ".eer", ".bz2"]


@pytest.mark.frame
@pytest.mark.metadata
@pytest.mark.parametrize("run_name", pytest.run_name, scope="session")
class TestFrame(HelperTestMRCHeader):
    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_header_class_variables(
        self,
        frames_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]],
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

    def test_frames_dimensions(self, frames_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]]):
        """Check that the frame dimensions are consistent."""
        errors = []
        frames_dimensions = None

        for _, header in frames_headers.items():
            if isinstance(header, list) and isinstance(header[0], tifffile.TiffPage):
                curr_dimensions = header[0].shape
                # first ensure all pages have the same dimensions
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
            else:
                errors.append(f"Unsupported frame type: {type(header)}")

        assert not errors, "\n".join(errors)

    ### END Self-consistency tests ###

    ### BEGIN Tiltseries consistency tests ###
    def test_frames_count(self, frames_files: List[str], tiltseries_metadata: Dict):
        assert len(frames_files) >= tiltseries_metadata["frames_count"]

    def test_frames_mdoc(
        self,
        frames_files: List[str],
        tiltseries_mdoc: pd.DataFrame,
        tiltseries_metadata: Dict,
    ):
        """Check that the tiltseries mdoc file contains the expected number of frames and that all listed frames exist."""
        assert len(tiltseries_mdoc) <= tiltseries_metadata["frames_count"]

        missing_frames = []
        remaining_frames_files_basenames = [os.path.basename(f) for f in frames_files]
        for _, row in tiltseries_mdoc.iterrows():
            frame_file = os.path.basename(str(row["SubFramePath"]).replace("\\", "/"))
            if frame_file not in remaining_frames_files_basenames:
                missing_frames.append(frame_file)
            else:
                remaining_frames_files_basenames.remove(frame_file)

        assert not missing_frames, f"Missing frames: {missing_frames}"

    ### END Tiltseries consistency tests ###
