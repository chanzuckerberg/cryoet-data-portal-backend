import pytest
from data_validation.shared.helper.mdoc_helper import MdocTestHelper


@pytest.mark.mdoc
@pytest.mark.parametrize("dataset, run_name", pytest.cryoet.dataset_run_combinations, scope="session")
class TestFrameAcquisitionFile(MdocTestHelper):

    pass
