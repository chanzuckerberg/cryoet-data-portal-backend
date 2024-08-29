import os

import allure
import pytest

from common.fs import FileSystemApi


@pytest.mark.voxel_spacing
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestVoxelSpacing:
    @allure.title("Voxel spacings match actual voxel spacing folders.")
    def test_voxel_spacing_parent_folder(
        self,
        tomograms_dir: str,
        filesystem: FileSystemApi,
        run_name: str,
        voxel_spacing: str,
    ):
        # not used, but pytest expects voxel_spacing to be used, otherwise it will throw an error
        del voxel_spacing
        actual_voxel_spacings_path = filesystem.glob(os.path.join(tomograms_dir, "*"))
        actual_voxel_spacings_names = [os.path.basename(path) for path in actual_voxel_spacings_path]
        expected_voxel_spacings = [
            run_spacing[1] for run_spacing in pytest.run_spacing_combinations if run_spacing[0] == run_name
        ]
        expected_voxel_spacings_names = [f"VoxelSpacing{path}" for path in expected_voxel_spacings]

        assert actual_voxel_spacings_names == expected_voxel_spacings_names

    @allure.title("Sanity check voxel spacing values.")
    def test_voxel_spacing(self, voxel_spacing: str, run_name: str, dataset: str):
        # not used, but pytest expects run_name to be used, otherwise it will throw an error
        del run_name
        # not used, but to ensure allure is properly generated (with this test being under the dataset tab in the "Behaviors" tab)
        del dataset
        voxel_spacing = float(voxel_spacing)
        assert voxel_spacing > 1
        assert voxel_spacing < 30
        assert pytest.approx(voxel_spacing % 1, abs=0.001) != 0  # shouldn't be a whole number
