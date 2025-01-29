import allure
import pytest

from data_validation.shared.helper.mdoc_helper import MdocTestHelper


@pytest.mark.mdoc
@pytest.mark.parametrize("run", pytest.cryoet.runs, ids=[ts.name for ts in pytest.cryoet.runs], scope="session")
class TestFrameAcquisitionFile(MdocTestHelper):

    @allure.title("Mdoc file exists when frames or tiltseries are present")
    def test_mdoc_file_count(self, mdoc_file: str, frames_files: list[str], tiltseries_files: list[str]):
        if frames_files or tiltseries_files:
            assert mdoc_file  is not None
        else:
            pytest.skip("No tiltseries or frame files")
