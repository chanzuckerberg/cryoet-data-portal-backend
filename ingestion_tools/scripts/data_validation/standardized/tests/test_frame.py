from typing import Dict, List, Union

import pytest
import tifffile
from mrcfile.mrcinterpreter import MrcInterpreter

from data_validation.shared.helper.twodee_helper import FrameTestHelper


@pytest.mark.frame
@pytest.mark.parametrize("dataset, run_name", pytest.cryoet.dataset_run_combinations, scope="session")
class TestFrame(FrameTestHelper):
    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_header_class_variables(
        self,
        frames_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]],
    ):
        self.mrc_headers = {k: v for k, v in frames_headers.items() if isinstance(v, MrcInterpreter)}
