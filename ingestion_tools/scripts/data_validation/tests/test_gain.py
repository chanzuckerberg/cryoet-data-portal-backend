import warnings
from typing import Dict, List, Union

import allure
import pytest
import tifffile
from mrcfile.mrcinterpreter import MrcInterpreter
from tests.helper_mrc import HelperTestMRCHeader, mrc_allure_title
from tests.test_frame import PERMITTED_FRAME_EXTENSIONS, helper_tiff_mrc_consistent

PERMITTED_GAIN_EXTENSIONS = PERMITTED_FRAME_EXTENSIONS + [".gain"]


@pytest.mark.gain
@pytest.mark.parametrize("dataset, run_name", pytest.dataset_run_combinations, scope="session")
class TestGain(HelperTestMRCHeader):
    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_header_class_variables(
        self,
        gain_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]],
    ):
        self.spacegroup = 0  # 2D image
        self.mrc_headers = {k: v for k, v in gain_headers.items() if isinstance(v, MrcInterpreter)}

    ### DON'T RUN SOME MRC HEADER TESTS ###
    @mrc_allure_title
    def test_nlabel(self):
        pytest.skip("Not applicable for gain files")

    @mrc_allure_title
    def test_nversion(self):
        pytest.skip("Not applicable for gain files")

    @mrc_allure_title
    def test_datatype(self):
        pytest.skip("Not applicable for gain files")

    @mrc_allure_title
    def test_mrc_spacing(self):
        pytest.skip("Not applicable for gain files")

    ### BEGIN Self-consistency tests ###
    @allure.title("Gain: files have valid extensions.")
    def test_extensions(self, gain_files: List[str]):
        errors = []

        for gain_file in gain_files:
            if not any(gain_file.endswith(ext) for ext in PERMITTED_FRAME_EXTENSIONS):
                errors.append(f"Invalid frame file extension: {gain_file}")

        if errors:
            warnings.warn("\n".join(errors), stacklevel=2)

    @allure.title("Gain: consistent dimensions and pixel spacings (MRC & TIFF).")
    def test_consistent(self, gain_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]]):
        return helper_tiff_mrc_consistent(gain_headers)

    ### END Self-consistency tests ###

    ### BEGIN Frame-specific tests ###
    @allure.title("Gain: same dimensions as the frames.")
    def test_matches_frame_dimensions(self, frames_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]]):
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

    @allure.title("Gain: same pixel spacing as the frames.")
    def test_tiltseries_pixel_spacing(
        self,
        gain_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]],
        frames_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]],
    ):
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
        else:
            pytest.skip("No MRC files found to compare pixel spacing")

    ### END Frame-specific tests ###
