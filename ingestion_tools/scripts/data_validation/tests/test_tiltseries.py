from typing import Dict

import pytest
from mrcfile.mrcinterpreter import MrcInterpreter
from tests.helper_mrc_zarr import HelperTestMRCZarrHeader


# By setting this scope to session, scope="session" fixtures will be reinitialized for each run + voxel_spacing combination
@pytest.mark.tiltseries
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestTiltseries(HelperTestMRCZarrHeader):

    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_zarr_header_class_variables(
        self,
        tiltseries_mrc_header: Dict[str, MrcInterpreter],
        tiltseries_zarr_header: Dict[str, Dict[str, Dict]],
        voxel_spacing: float,
    ):
        self.spacegroup = 0  # 2D image
        self.mrc_headers = tiltseries_mrc_header
        self.zarr_headers = tiltseries_zarr_header
        self.voxel_spacing = voxel_spacing
        self.skip_z_axis_checks = True
