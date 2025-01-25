import warnings

import pytest
from mrcfile.mrcinterpreter import MrcInterpreter
from tifffile import TiffPage

from data_validation.helpers.helper_mrc import HelperTestMRCHeader
from data_validation.helpers.helper_tiff_mrc import helper_tiff_mrc_consistent
from data_validation.helpers.util import PERMITTED_FRAME_EXTENSIONS


@pytest.mark.frame
@pytest.mark.parametrize("run", pytest.cryoet.runs, ids=[ts.name for ts in pytest.cryoet.runs], scope="session")
class TestFrame(HelperTestMRCHeader):

    @pytest.fixture(scope="class")
    def frame_mrc_headers(self, frames_headers: dict[str, list[TiffPage]| MrcInterpreter]) -> dict[str, MrcInterpreter]:
        return {k: v for k, v in frames_headers.items() if isinstance(v, MrcInterpreter)}

    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_header_class_variables(self, frame_mrc_headers: dict[str, MrcInterpreter]):
        self.spacegroup = 0  # 2D image
        self.mrc_headers = frame_mrc_headers.items()

    ### DON'T RUN SOME MRC HEADER TESTS ###
    def test_nlabel(self):
        pytest.skip("Not applicable for frame files")

    def test_nversion(self):
        pytest.skip("Not applicable for frame files")

    def test_mrc_spacing(self):
        pytest.skip("Not applicable for frame files")

    ### BEGIN Self-consistency tests ###
    def test_extensions(self, frame_files: list[str]):
        errors = []
        for frame_file in frame_files:
            if not any(frame_file.endswith(ext) for ext in PERMITTED_FRAME_EXTENSIONS):
                errors.append(f"Invalid frame file extension: {frame_file}")

        if errors:
            warnings.warn("\n".join(errors), stacklevel=2)

    def test_consistent(self):
        return helper_tiff_mrc_consistent(self.mrc_headers)

    ### END Self-consistency tests ###
