import allure
import pandas as pd
import pytest
import tifffile
from data_validation.shared.helper.tilt_angles_helper import TiltAnglesHelper
from mrcfile.mrcinterpreter import MrcInterpreter


@pytest.mark.tilt_angles
@pytest.mark.parametrize("dataset, run_name, ts_dir", pytest.cryoet.dataset_run_tiltseries_combinations, scope="session")
class TestTiltAngles(TiltAnglesHelper):
    """
    A class to test tilt angle data. Only checking that the # of angles in these files are consistent with other files /
    data and that they properly map to other files / data. Other data validation tests is done in respective classes.
    Spans .tlt, .rawtlt, .mdoc, tiltseries_metadata.json, frames files.
    Ordering:
        - .tlt (<=) maps to .rawtlt (not necessarily 1:1)
        - .rawtlt (<=) maps to .mdoc (not necessarily 1:1)
        - tiltseries metadata size["z"] == number of rawtlt entries
    """

    ### BEGIN Raw Tilt .rawtlt tests ###

    @allure.title(
        "Raw tilt: number of raw tilt angles are less than or equal to tiltseries size['z'] (implied to be the number of frames files).",
    )
    def test_raw_tilt_tiltseries_metadata(self, raw_tilt_data: pd.DataFrame, tiltseries_metadata: dict):
        assert len(raw_tilt_data) <= tiltseries_metadata["size"]["z"]


    ### BEGIN Tiltseries consistency tests ###
    @allure.title("Frames: tiltseries pixel spacing is an integer multiple of the frame pixel spacing.")
    def test_tiltseries_pixel_spacing(
        self,
        dataset: str,
        frames_headers: dict[str, list[tifffile.TiffPage] | MrcInterpreter],
        tiltseries_metadata: dict,
    ):
        for frame_file, frame_header in frames_headers.items():
            if isinstance(frame_header, MrcInterpreter):
                # only need to check the first frame, since we check that all frames have the same pixel spacing
                assert tiltseries_metadata["pixel_spacing"] / frame_header.voxel_size["x"] == pytest.approx(
                    round(tiltseries_metadata["pixel_spacing"] / frame_header.voxel_size["y"]),
                    abs=0.001,
                ), f"Pixel spacing does not match tiltseries metadata, {frame_file}"
                return

    ### END Tiltseries consistency tests ###
