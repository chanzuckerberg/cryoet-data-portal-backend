import re

import allure
import pytest


@pytest.mark.voxel_spacing
@pytest.mark.parametrize("dataset, run_name, voxel_spacing", pytest.cryoet.dataset_run_spacing_combinations, scope="session")
class TestVoxelSpacing:
    @allure.title("Voxel spacing: Sanity check voxel spacing values.")
    def test_voxel_spacing(self, voxel_spacing: str, run_name: str, dataset: str):
        # both not used, but to ensure allure is properly generated (with this test being under the dataset tab in the "Behaviors" tab)
        del run_name, dataset
        assert re.match(r"^\d+.\d{3}$", voxel_spacing)
        voxel_spacing = float(voxel_spacing)
        assert voxel_spacing > 1
        assert voxel_spacing < 30
        assert pytest.approx(voxel_spacing % 1, abs=0.001) != 0  # shouldn't be a whole number
