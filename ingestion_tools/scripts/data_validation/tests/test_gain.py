import warnings
from typing import Dict, List, Union

import pytest
import tifffile
from data_validation.tests.helper_mrc import HelperTestMRCHeader
from data_validation.tests.test_frame import PERMITTED_FRAME_EXTENSIONS, helper_tiff_mrc_consistent
from mrcfile.mrcinterpreter import MrcInterpreter

PERMITTED_GAIN_EXTENSIONS = PERMITTED_FRAME_EXTENSIONS + [".gain"]


@pytest.mark.gain
@pytest.mark.metadata
@pytest.mark.parametrize("run_name", pytest.run_name, scope="session")
class TestGain(HelperTestMRCHeader):
    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_header_class_variables(
        self,
        gain_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]],
    ):
        self.spacegroup = 0  # 2D image
        self.mrc_headers = {k: v for k, v in gain_headers.items() if isinstance(v, MrcInterpreter)}

    ### DON'T RUN SOME MRC HEADER TESTS ###
    def test_nlabel(self):
        pytest.skip("Not applicable for gain files")

    def test_nversion(self):
        pytest.skip("Not applicable for gain files")

    def test_mrc_mode(self):
        pytest.skip("Not applicable for gain files")

    def test_mrc_spacing(self):
        pytest.skip("Not applicable for gain files")

    ### BEGIN Self-consistency tests ###
    def test_gain_format(self, gain_files: List[str]):
        errors = []

        for gain_file in gain_files:
            if not any(gain_file.endswith(ext) for ext in PERMITTED_FRAME_EXTENSIONS):
                errors.append(f"Invalid frame file extension: {gain_file}")

        if errors:
            warnings.warn("\n".join(errors), stacklevel=2)

    def test_gain_consistent(self, gain_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]]):
        return helper_tiff_mrc_consistent(gain_headers)

    def test_gain_nz(self):
        def check_nz(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            assert header.nz == 1  # 2D image

        self.mrc_header_helper(check_nz)

    ### END Self-consistency tests ###

    ### BEGIN Frame-specific tests ###
    def test_gain_frames(
        self,
        gain_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]],
        frames_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]],
    ):
        """Check that the gain pixel spacing & dimensions matches the frame pixel spacing. Just need to check first MRC file of each."""

        first_mrc_gain = None
        for _, gain_header in gain_headers.items():
            if isinstance(gain_header, MrcInterpreter):
                first_mrc_gain = gain_header
                break

        first_mrc_frame = None
        for _, frame_header in frames_headers.items():
            if isinstance(frame_header, MrcInterpreter):
                first_mrc_frame = frame_header
                break

        if first_mrc_gain and first_mrc_frame:
            assert first_mrc_gain.voxel_size["x"] == first_mrc_frame.voxel_size["x"]
            assert first_mrc_gain.voxel_size["y"] == first_mrc_frame.voxel_size["y"]
            assert first_mrc_gain.header.nx == first_mrc_frame.header.nx
            assert first_mrc_gain.header.ny == first_mrc_frame.header.ny
        else:
            pytest.skip("No MRC files found to compare pixel spacing")

    ### END Frame-specific tests ###
