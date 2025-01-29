import allure
import pytest

from data_validation.shared.helper.tilt_angles_helper import TiltAnglesHelper


@pytest.mark.tilt_angles
@pytest.mark.parametrize("run", pytest.cryoet.runs, ids=[ts.name for ts in pytest.cryoet.runs], scope="session")
class TestTiltAngles(TiltAnglesHelper):

    @allure.title("Raw tilt: file exists when tiltseries present")
    def test_raw_tlt_file_exists(self, raw_tlt_file: str, tiltseries_files: list[str]):
        if tiltseries_files:
            assert raw_tlt_file is not None
        else:
            pytest.skip("No tiltseries exists")
