
import pytest
from data_validation.shared.helper.twodee_helper import FrameTestHelper


@pytest.mark.frame
@pytest.mark.parametrize("dataset, run_name", pytest.cryoet.dataset_run_combinations, scope="session")
class TestFrame(FrameTestHelper):
    pass
