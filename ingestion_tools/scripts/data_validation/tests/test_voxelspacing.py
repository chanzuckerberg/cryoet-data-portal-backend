import os

import pytest

from common.fs import FileSystemApi


@pytest.mark.voxel_spacing
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestVoxelSpacing:
    def test_voxel_spacing_parent_folder(
        self,
        tomograms_dir: str,
        filesystem: FileSystemApi,
        run_name: str,
        voxel_spacing: float,
    ):
        actual_voxel_spacings = filesystem.glob(os.path.join(tomograms_dir, "*"))
        actual_voxel_spacings_names = [os.path.basename(i) for i in actual_voxel_spacings]
        expected_voxel_spacings = [i[1] for i in pytest.run_spacing_combinations if i[0] == run_name]
        expected_voxel_spacings_names = [f"VoxelSpacing{i:.3f}" for i in expected_voxel_spacings]

        assert actual_voxel_spacings_names == expected_voxel_spacings_names

    def test_voxel_spacing(self, voxel_spacing: float, run_name: str):
        assert voxel_spacing > 1
        assert voxel_spacing < 30
        assert pytest.approx(voxel_spacing % 1, abs=0.001) != 0  # shouldn't be a whole number
