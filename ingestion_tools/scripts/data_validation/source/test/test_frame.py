import warnings

import pytest
from importers.frame import FrameImporter

from data_validation.helpers.helper_mrc import HelperTestMRCHeader
from data_validation.helpers.helper_tiff_mrc import helper_tiff_mrc_consistent
from data_validation.helpers.util import PERMITTED_FRAME_EXTENSIONS, get_file_type, get_mrc_header


@pytest.mark.frame
@pytest.mark.parametrize("frame", pytest.cryoet.frames, ids=[ts.name for ts in pytest.cryoet.frames], scope="session")
class TestFrame(HelperTestMRCHeader):

    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_header_class_variables(self, frame: FrameImporter):
        self.spacegroup = 0  # 2D image
        self.file_type = get_file_type(frame.name)
        if frame.allow_imports and self.file_type == "mrc":
            file_path = frame.path
            self.mrc_headers = {file_path: get_mrc_header(file_path, frame.config.fs, fail_test=False)}

    ### DON'T RUN SOME MRC HEADER TESTS ###
    def test_nlabel(self):
        pytest.skip("Not applicable for frame files")

    def test_nversion(self):
        pytest.skip("Not applicable for frame files")

    def test_mrc_spacing(self):
        pytest.skip("Not applicable for frame files")

    ### BEGIN Self-consistency tests ###
    def test_extensions(self, frame: FrameImporter):
        frame_file = frame.path
        if not any(frame_file.endswith(ext) for ext in PERMITTED_FRAME_EXTENSIONS):
            warnings.warn(f"Invalid frame file extension: {frame_file}", stacklevel=2)

    def test_consistent(self):
        return helper_tiff_mrc_consistent(self.mrc_headers)
