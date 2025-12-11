import allure
import pandas as pd
import pytest
from data_validation.shared.helper.mdoc_helper import MdocTestHelper


@pytest.mark.mdoc
@pytest.mark.parametrize("dataset, run_name", pytest.cryoet.dataset_run_combinations, scope="session")
class TestFrameAcquisitionFile(MdocTestHelper):

    @allure.title("Mdoc: number of mdoc sections, equal number of frames files, equals number of items in frames metadata.")
    def test_mdoc_frames(self, mdoc_data: pd.DataFrame, frames_files: list[str], frame_metadata: dict[str, dict]):
        frames_len = len(frames_files)
        if frames_len == 0:
            pytest.skip("No frame files to compare")
        frames_metadata_len = len(frame_metadata["frames"])
        mdoc_len = len(mdoc_data)
        assert mdoc_len == frames_len == frames_metadata_len, f"Number of mdoc sections {mdoc_len} mismatches number of frames: {frames_len} or frames metadata: {frames_metadata_len}"
