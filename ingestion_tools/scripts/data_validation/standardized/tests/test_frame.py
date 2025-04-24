from typing import Dict, List, Union

import allure
import pytest
import tifffile
from data_validation.shared.helper.twodee_helper import FrameTestHelper
from mrcfile.mrcinterpreter import MrcInterpreter


@pytest.mark.frame
@pytest.mark.parametrize("dataset, run_name", pytest.cryoet.dataset_run_combinations, scope="session")
class TestFrame(FrameTestHelper):
    @allure.title("Frames: When isGainCorrected == False, a Gains entity exists for the run")
    def test_is_gain_corrected_false(self,
                         frame_metadata: Dict,
                         gain_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]], # this is skipped if it is not found
                         ):
        if not frame_metadata.get("is_gain_corrected"):
            assert len(gain_headers) > 0

    @allure.title("Frames: max(acquisitionOrder) <= number of frames -1")
    def test_max_acquisition_order(self, frame_metadata: Dict):
        acquisition_order_max = max(f.get("acquisition_order", 0) for f in frame_metadata["frames"])
        assert acquisition_order_max <= len(frame_metadata["frames"]) - 1

    @allure.title("Frames: Sorting acquisitionOrder low-to-high and accumulatedDose low-to-high results in the same order")
    def test_sorting_acquisition_order_and_accumulated_dose(self, frame_metadata: Dict):
        frames = frame_metadata["frames"]
        frames_sorted_by_acquisition_order = sorted(frames, key=lambda f: (f["acquisition_order"]))
        frames_sorted_by_accumulated_dose = sorted(frames, key=lambda f: (f["accumulated_dose"]))
        assert frames_sorted_by_acquisition_order == frames_sorted_by_accumulated_dose
