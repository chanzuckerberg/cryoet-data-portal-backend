import re
from typing import Any

import allure
import numpy as np
import pandas as pd
import pytest
from data_validation.shared.helper.helper_mrc_zarr import HelperTestMRCZarrHeader

TILT_AXIS_ANGLE_REGEX = re.compile(r".*tilt\s*axis\s*angle\s*=\s*([-+]?(?:\d*\.*\d+))")



@pytest.fixture
def mdoc_tilt_axis_angle(mdoc_data: pd.DataFrame) -> float:
    # To convert the data from the mdoc into a data frame, all the global records are added to each section's data
    titles = mdoc_data["titles"][0]
    for title in titles:
        if result := re.match(TILT_AXIS_ANGLE_REGEX, title.lower()):
            return float(result[1])
    pytest.fail("No Tilt axis angle found")


class TiltSeriesHelper(HelperTestMRCZarrHeader):

    @pytest.fixture(autouse=True)
    def set_space_group(self):
        self.spacegroup = 0  # 2D image

    @pytest.fixture
    def tiltseries_metadata_range(self, tiltseries_metadata: dict) -> list[float]:
        # add tilt_step to max because arange is end value exclusive
        return np.arange(
            tiltseries_metadata["tilt_range"]["min"],
            tiltseries_metadata["tilt_range"]["max"] + tiltseries_metadata["tilt_step"],
            tiltseries_metadata["tilt_step"],
        ).tolist()

    @allure.title("Tiltseries: tilt axis angle in mdoc file matches that in tilt series metadata (+/- 10 deg).")
    def test_tilt_axis_angle(self, mdoc_tilt_axis_angle: float, tiltseries_metadata: dict[str, Any]):
        metadata_tilt_axis = tiltseries_metadata["tilt_axis"]
        assert (abs(
            metadata_tilt_axis - mdoc_tilt_axis_angle) <= 10
        ), f"Tilt axis angle mismatch: MDOC: {mdoc_tilt_axis_angle} vs Metadata: {metadata_tilt_axis}"
