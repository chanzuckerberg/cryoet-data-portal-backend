import warnings
from typing import Dict, List, Union

import allure
import pytest
import tifffile
from data_validation.shared.helper.helper_mrc import HelperTestMRCHeader, mrc_allure_title
from data_validation.shared.helper.helper_tiff_mrc import helper_tiff_mrc_consistent
from data_validation.shared.util import PERMITTED_FRAME_EXTENSIONS
from mrcfile.mrcinterpreter import MrcInterpreter


class TwoDeeFileTestHelper(HelperTestMRCHeader):

    @pytest.fixture(autouse=True)
    def set_space_group(self):
        self.spacegroup = 0  # 2D image

    ### DON'T RUN SOME MRC HEADER TESTS ###
    @mrc_allure_title
    def test_nlabel(self):
        pytest.skip(f"Not applicable for {self.entity_type} files")

    @mrc_allure_title
    def test_nversion(self):
        pytest.skip(f"Not applicable for {self.entity_type} files")

    @mrc_allure_title
    def test_mrc_spacing(self):
        pytest.skip(f"Not applicable for {self.entity_type} files")

    ### BEGIN Self-consistency tests ###
    def test_extensions(self, frames_files: List[str]):
        errors = []

        for frame_file in frames_files:
            if not any(frame_file.endswith(ext) for ext in self.permitted_extensions):
                errors.append(f"Invalid {self.entity_type} file extension: {frame_file}")

        if errors:
            warnings.warn("\n".join(errors), stacklevel=2)

    def test_consistent(self, frames_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]]):
        return helper_tiff_mrc_consistent(frames_headers)
    ### END Self-consistency tests ###


class FrameTestHelper(TwoDeeFileTestHelper):

    @pytest.fixture(autouse=True)
    def set_entity_variables(self, frames_headers: dict[str, MrcInterpreter]):
        self.entity_type = "frame"
        self.permitted_extensions = PERMITTED_FRAME_EXTENSIONS
        self.mrc_headers = {k: v for k, v in frames_headers.items() if isinstance(v, MrcInterpreter)}
        if not self.mrc_headers:
            self.error_on_no_mrc_header = False

    ### BEGIN Self-consistency tests ###
    @allure.title("Frames: valid extensions.")
    def test_extensions(self, frames_files: List[str]):
       super().test_extensions(frames_files)

    @allure.title("Frames: consistent dimensions and pixel spacings (MRC & TIFF).")
    def test_consistent(self, frames_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]]):
        super().test_consistent(frames_headers)
    ### END Self-consistency tests ###


class GainTestHelper(TwoDeeFileTestHelper):

    @pytest.fixture(autouse=True)
    def set_entity_variables(self, gain_headers: dict[str, MrcInterpreter]):
        self.entity_type = "gain"
        self.mrc_headers = gain_headers
        if not self.mrc_headers:
            self.error_on_no_mrc_header = False

    ### BEGIN Self-consistency tests ###
    @allure.title("Gain: valid extensions.")
    def test_extensions(self, gain_files: List[str]):
       super().test_extensions(gain_files)

    @allure.title("Gain: consistent dimensions and pixel spacings (MRC & TIFF).")
    def test_consistent(self, gain_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]]):
        super().test_consistent(gain_headers)

    def test_gain_nz(self):
        def check_nz(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            assert header.nz == 1  # 2D image

        self.mrc_header_helper(check_nz)
    ### END Self-consistency tests ###
