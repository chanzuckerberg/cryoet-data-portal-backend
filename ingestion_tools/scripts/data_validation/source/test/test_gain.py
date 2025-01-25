import warnings

import pytest
import tifffile
from importers.gain import GainImporter
from importers.run import RunImporter
from mrcfile.mrcinterpreter import MrcInterpreter

from common.fs import S3Filesystem
from data_validation.helpers.helper_mrc import HelperTestMRCHeader
from data_validation.helpers.helper_tiff_mrc import helper_tiff_mrc_consistent
from data_validation.helpers.util import (
    MRC_EXTENSION,
    PERMITTED_GAIN_EXTENSIONS,
    get_mrc_header,
)

PERMITTED_SOURCE_GAIN_EXTENSIONS = PERMITTED_GAIN_EXTENSIONS + [".dm4"]


@pytest.mark.gain
@pytest.mark.parametrize("run", pytest.cryoet.runs, ids=[ts.name for ts in pytest.cryoet.runs], scope="session")
class TestGain(HelperTestMRCHeader):

    @pytest.fixture(scope="class")
    def gain_files(self, run: RunImporter) -> list[str]:
        return pytest.cryoet.get_importable_entities(GainImporter, [run], "path")

    @pytest.fixture(scope="class")
    def gain_headers(
            self, gain_files: list[str], filesystem: S3Filesystem,
    ) -> dict[str, list[tifffile.TiffPage]| MrcInterpreter]:
        """Get the mrc file headers for a gain file."""
        return {
            file_path: get_mrc_header(file_path, filesystem, fail_test=False)
            for file_path in gain_files if file_path.endswith(MRC_EXTENSION)
        }

    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_header_class_variables(
            self, gain_headers: dict[str, list[tifffile.TiffPage]| MrcInterpreter],
    ):
        self.spacegroup = 0  # 2D image
        self.mrc_headers = gain_headers

    ### DON'T RUN SOME MRC HEADER TESTS ###
    def test_nlabel(self):
        pytest.skip("Not applicable for gain files")

    def test_nversion(self):
        pytest.skip("Not applicable for gain files")

    def test_mrc_spacing(self):
        pytest.skip("Not applicable for gain files")

    ### BEGIN Self-consistency tests ###
    def test_extensions(self, gain_files: list[str]):
        errors = []

        for gain_file in gain_files:
            if not any(gain_file.endswith(ext) for ext in PERMITTED_GAIN_EXTENSIONS):
                errors.append(f"Invalid gain file extension: {gain_file}")

        if errors:
            warnings.warn("\n".join(errors), stacklevel=2)


    def test_consistent(self, gain_headers: dict[str, list[tifffile.TiffPage]| MrcInterpreter]):
        return helper_tiff_mrc_consistent(gain_headers)

    def test_gain_nz(self):
        def check_nz(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            assert header.nz == 1  # 2D image

        self.mrc_header_helper(check_nz)

    ### END Self-consistency tests ###
