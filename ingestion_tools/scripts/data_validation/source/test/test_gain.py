import pytest
import tifffile
from data_validation.shared.helper.twodee_helper import GainTestHelper
from data_validation.shared.util import (
    MRC_EXTENSION,
    PERMITTED_GAIN_EXTENSIONS,
    get_mrc_header,
)
from importers.gain import GainImporter
from importers.run import RunImporter
from mrcfile.mrcinterpreter import MrcInterpreter

from common.fs import S3Filesystem

PERMITTED_SOURCE_GAIN_EXTENSIONS = PERMITTED_GAIN_EXTENSIONS + [".dm4"]


@pytest.mark.gain
@pytest.mark.parametrize("run", pytest.cryoet.runs, ids=[ts.name for ts in pytest.cryoet.runs], scope="session")
class TestGain(GainTestHelper):

    @pytest.fixture(scope="class")
    def gain_files(self, run: RunImporter) -> list[str]:
        return pytest.cryoet.get_importable_entities(GainImporter, [run], "path")

    @pytest.fixture(autouse=True)
    def set_valid_extensions(self):
        self.permitted_extensions = PERMITTED_GAIN_EXTENSIONS + [".dm4"]

    @pytest.fixture(scope="class")
    def gain_headers(
            self, gain_files: list[str], filesystem: S3Filesystem,
    ) -> dict[str, list[tifffile.TiffPage]| MrcInterpreter]:
        """Get the mrc file headers for a gain file."""
        return {
            file_path: get_mrc_header(file_path, filesystem, fail_test=False)
            for file_path in gain_files if file_path.endswith(MRC_EXTENSION)
        }
