import warnings

import pytest
import tifffile
from importers.gain import GainImporter
from mrcfile.mrcinterpreter import MrcInterpreter

from data_validation.helpers.helper_mrc import HelperTestMRCHeader
from data_validation.helpers.helper_tiff_mrc import helper_tiff_mrc_consistent
from data_validation.helpers.util import PERMITTED_GAIN_EXTENSIONS, get_file_type, get_mrc_header, get_tiff_mrc_headers

PERMITTED_SOURCE_GAIN_EXTENSIONS = PERMITTED_GAIN_EXTENSIONS + [".dm4"]


@pytest.mark.gain
@pytest.mark.parametrize("gain", pytest.cryoet.gains, ids=[ts.name for ts in pytest.cryoet.gains], scope="session")
class TestGain(HelperTestMRCHeader):

    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_header_class_variables(self, gain: GainImporter):
        self.spacegroup = 0  # 2D image

        self.file_type = get_file_type(gain.name)
        file_path = gain.path
        if gain.allow_imports and self.file_type == "mrc":
            self.mrc_headers = {file_path: get_mrc_header(file_path, gain.config.fs, fail_test=False)}

    @pytest.fixture(scope="session")
    def gain_headers(self, gain: GainImporter) -> dict[str, list[tifffile.TiffPage]| MrcInterpreter]:
        """Get the mrc file headers for a gain file."""
        return get_tiff_mrc_headers([gain.path], gain.config.fs)

    ### DON'T RUN SOME MRC HEADER TESTS ###
    def test_nlabel(self):
        pytest.skip("Not applicable for gain files")

    def test_nversion(self):
        pytest.skip("Not applicable for gain files")

    def test_mrc_spacing(self):
        pytest.skip("Not applicable for gain files")

    ### BEGIN Self-consistency tests ###
    def test_extensions(self, gain: GainImporter):
        gain_file = gain.path
        if not any(gain_file.endswith(ext) for ext in PERMITTED_SOURCE_GAIN_EXTENSIONS):
            warnings.warn(f"Invalid gain file extension: {gain_file}", stacklevel=2)

    def test_consistent(self, gain_headers: dict[str, list[tifffile.TiffPage]| MrcInterpreter]):
        return helper_tiff_mrc_consistent(gain_headers)

    def test_gain_nz(self):
        def check_nz(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            assert header.nz == 1  # 2D image

        self.mrc_header_helper(check_nz)

    ### END Self-consistency tests ###
