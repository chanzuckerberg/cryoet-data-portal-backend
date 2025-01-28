import pytest
from mrcfile.mrcinterpreter import MrcInterpreter
from tifffile import TiffPage

from data_validation.shared.helper.frame_helper import FrameTestHelper


@pytest.mark.frame
@pytest.mark.parametrize("run", pytest.cryoet.runs, ids=[ts.name for ts in pytest.cryoet.runs], scope="session")
class TestFrame(FrameTestHelper):

    @pytest.fixture(scope="class")
    def frame_mrc_headers(self, frames_headers: dict[str, list[TiffPage]| MrcInterpreter]) -> dict[str, MrcInterpreter]:
        return {k: v for k, v in frames_headers.items() if isinstance(v, MrcInterpreter)}

    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_header_class_variables(self, frame_mrc_headers: dict[str, MrcInterpreter]):
        self.mrc_headers = frame_mrc_headers.items()
