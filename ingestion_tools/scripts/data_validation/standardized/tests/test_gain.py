from typing import Dict, List, Union

import allure
import pytest
import tifffile
from mrcfile.mrcinterpreter import MrcInterpreter

from data_validation.shared.helper.twodee_helper import GainTestHelper


@pytest.mark.gain
@pytest.mark.parametrize("dataset, run_name", pytest.cryoet.dataset_run_combinations, scope="session")
class TestGain(GainTestHelper):

    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_header_class_variables(
        self,
        gain_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]],
    ):
        self.mrc_headers = {k: v for k, v in gain_headers.items() if isinstance(v, MrcInterpreter)}

    ### BEGIN Frame-specific tests ###
    @allure.title("Gain: pixel spacing and dimensions match frames.")
    def test_gain_frames(
        self,
        gain_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]],
        frames_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]],
    ):
        first_mrc_gain = None
        for _, gain_header in gain_headers.items():
            if isinstance(gain_header, MrcInterpreter):
                first_mrc_gain = gain_header
                break

        first_mrc_frame = None
        for _, frame_header in frames_headers.items():
            if isinstance(frame_header, MrcInterpreter):
                first_mrc_frame = frame_header
                break

        if first_mrc_gain and first_mrc_frame:
            assert first_mrc_gain.voxel_size["x"] == first_mrc_frame.voxel_size["x"]
            assert first_mrc_gain.voxel_size["y"] == first_mrc_frame.voxel_size["y"]
            assert first_mrc_gain.header.nx == first_mrc_frame.header.nx
            assert first_mrc_gain.header.ny == first_mrc_frame.header.ny
        else:
            pytest.skip("No MRC files found to compare pixel spacing")

    ### END Frame-specific tests ###
