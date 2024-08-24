from typing import Dict, List, Union

import pytest
import tifffile
from mrcfile.mrcinterpreter import MrcInterpreter
from tests.helper_mrc import HelperTestMRCHeader


@pytest.mark.gain
@pytest.mark.metadata
@pytest.mark.parametrize("run_name", pytest.run_name, scope="session")
class TestGain(HelperTestMRCHeader):
    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_header_class_variables(self, gain_mrc_header: Dict[str, MrcInterpreter]):
        self.spacegroup = 0  # 2D image
        self.mrc_headers = gain_mrc_header

    ### DON'T RUN SOME MRC HEADER TESTS ###
    def test_nlabel(self):
        pytest.skip("Not applicable for gain files")

    def test_nversion(self):
        pytest.skip("Not applicable for gain files")

    def test_mrc_mode(self):
        pytest.skip("Not applicable for gain files")

    def test_mrc_voxel_spacing(self):
        pytest.skip("Not applicable for gain files")

    ### BEGIN Self-consistency tests ###

    ### END Self-consistency tests ###

    ### BEGIN Frame-specific tests ###

    def test_matches_frame_dimensions(self, frames_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]]):
        """Check that the gain dimensions match the frame dimensions."""

        def check_matches_frame_dimensions(header, _interpreter, _mrc_filename, frame_dimensions):
            del _interpreter, _mrc_filename
            assert header.nx == frame_dimensions[0]
            assert header.ny == frame_dimensions[1]
            assert header.nz == 1  # 2D image

        # We only need to check the first frame, since we check that all frames have the same dimensions
        first_frame = list(frames_headers.values())[0]
        frame_dimensions = (
            (first_frame.nx, first_frame.ny)
            if isinstance(first_frame, MrcInterpreter)
            else (first_frame[0].imagewidth, first_frame[0].imagelength)
        )
        self.mrc_header_helper(check_matches_frame_dimensions, frame_dimensions=frame_dimensions)

    ### END Frame-specific tests ###
