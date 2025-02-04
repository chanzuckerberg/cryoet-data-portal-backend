import allure
import pytest
from data_validation.shared.helper.twodee_helper import FrameTestHelper


@pytest.mark.frame
@pytest.mark.parametrize("run", pytest.cryoet.runs, ids=[ts.name for ts in pytest.cryoet.runs], scope="session")
class TestFrame(FrameTestHelper):

    @allure.title("Mdoc file exists when frames are present")
    def test_frames_have_mdoc(self, frames_files: list[str], mdoc_file: str):
        if len(frames_files) == 0:
            pytest.skip("No frame files")
        assert mdoc_file is not None
