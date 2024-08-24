import os
from typing import Dict, List, Union

import pandas as pd
import pytest
import tifffile
from mrcfile.mrcinterpreter import MrcInterpreter
from tests.helper_mrc import HelperTestMRCHeader

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

    ### DON'T RUN SOME MRC HEADER TESTS ###
    def test_nlabel(self):
        pytest.skip("Not applicable for frame files")

    def test_nversion(self):
        pytest.skip("Not applicable for frame files")

    def test_mrc_mode(self):
        pytest.skip("Not applicable for frame files")

    def test_mrc_voxel_spacing(self):
        pytest.skip("Not applicable for frame files")

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

        for filename, header_entity in frames_headers.items():
            if isinstance(header_entity, list) and isinstance(header_entity[0], tifffile.TiffPage):
                curr_dimensions = header_entity[0].shape
                if not all(page.shape == curr_dimensions for page in header_entity):
                    errors.append(f"Not all pages have the same dimensions {filename}")

                if frames_dimensions is None:
                    frames_dimensions = curr_dimensions
                elif curr_dimensions != frames_dimensions:
                    errors.append(
                        f"Frame dimensions do not match: {curr_dimensions} != {frames_dimensions}, {filename}",
                    )
            elif isinstance(header_entity, MrcInterpreter):
                header = header_entity.header
                if frames_dimensions is None:
                    frames_dimensions = (header.nx, header.ny)
                elif (header.nx, header.ny) != frames_dimensions:
                    errors.append(
                        f"Frame dimensions do not match: ({header.nx}, {header.ny}) != {frames_dimensions}, {filename}",
                    )
            else:
                errors.append(f"Unsupported frame type: {type(header)}, {filename}")

        assert not errors, "\n".join(errors)

    ### END Self-consistency tests ###

    ### BEGIN Tiltseries consistency tests ###
    def test_frames_count(self, frames_files: List[str], tiltseries_metadata: Dict):
        assert len(frames_files) >= tiltseries_metadata["frames_count"]

    def test_mdoc_frame_paths_exist(
        self,
        frames_files: List[str],
        tiltseries_mdoc: pd.DataFrame,
    ):
        """Check that all mdoc listed frames exist (not all frames files have to be listed in mdoc though)."""
        missing_frames = []
        remaining_frames_files_basenames = [os.path.basename(f) for f in frames_files]
        for _, row in tiltseries_mdoc.iterrows():
            frame_file = os.path.basename(str(row["SubFramePath"]).replace("\\", "/"))
            if frame_file not in remaining_frames_files_basenames:
                missing_frames.append(frame_file)
            else:
                remaining_frames_files_basenames.remove(frame_file)

        assert not missing_frames, f"Missing frames: {missing_frames}"

    def test_frames_mdoc_numsubframes(
        self,
        frames_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]],
        tiltseries_mdoc: pd.DataFrame,
    ):
        """Check that all mdoc listed frames have the correct number of subframes (corresponds to the header info in the frame file)."""
        errors = []
        for _, row in tiltseries_mdoc.iterrows():
            frame_file = os.path.basename(str(row["SubFramePath"]).replace("\\", "/"))
            if frame_file not in frames_headers:
                # Frame file does not exist, this will get caught by another test
                continue

            header_entity = frames_headers[frame_file]
            if isinstance(header_entity, list) and isinstance(header_entity[0], tifffile.TiffPage):
                if len(header_entity) != row["NumSubFrames"]:
                    errors.append(
                        f"Number of subframes do not match: {len(header_entity)} != {row['NumSubFrames']}, {frame_file}",
                    )
            elif isinstance(header_entity, MrcInterpreter):
                if header_entity.header.nz != row["NumSubFrames"]:
                    errors.append(
                        f"Number of subframes do not match: {header_entity.header.nz} != {row['NumSubFrames']}, {frame_file}",
                    )
            else:
                errors.append(f"Unsupported frame type: {type(frame_file)}, {frame_file}")

        assert not errors, "\n".join(errors)

    ### END Tiltseries consistency tests ###
