import re
from typing import Any

import allure
import numpy as np
import pandas as pd
import pytest
from data_validation.shared.helper.helper_mrc_zarr import HelperTestMRCZarrHeader

TILT_AXIS_ANGLE_REGEX = re.compile(r".*tilt\s*axis\s*angle\s*=\s*([-+]?(?:\d*\.*\d+))")


def assert_angle_in_valid_range(angle: float, label: str) -> None:
    assert -360 <= angle <= 360, f"{label} {angle} is outside the valid range [-360, 360]."


def angular_difference(a: float, b: float) -> float:
    """Smallest absolute difference between two angles (degrees), wrapping around 360. Result in [0, 180]."""
    diff = abs(a - b) % 360
    return min(diff, 360 - diff)

class TiltSeriesHelper(HelperTestMRCZarrHeader):
    @pytest.fixture
    def mdoc_tilt_axis_angle(self, mdoc_data: pd.DataFrame) -> float:
        # To convert the data from the mdoc into a data frame, all the global records are added to each section's data
        titles = mdoc_data["titles"][0]
        for title in titles:
            if result := re.match(TILT_AXIS_ANGLE_REGEX, title.lower()):
                return float(result[1])
        pytest.fail("No Tilt axis angle found")

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
        assert_angle_in_valid_range(mdoc_tilt_axis_angle, "Mdoc tilt axis angle")
        assert_angle_in_valid_range(metadata_tilt_axis, "Metadata tilt axis angle")
        assert angular_difference(metadata_tilt_axis, mdoc_tilt_axis_angle) <= 10, (
            f"Tilt axis angle mismatch: MDOC: {mdoc_tilt_axis_angle} vs Metadata: {metadata_tilt_axis}"
        )
