import pytest


class BaseAnnotation:
    @pytest.fixture(autouse=True)
    def _set_info(self, dataset, run_name, voxel_spacing):
        """Set the dataset and run name for the tests."""
        self.dataset = dataset
        self.run_name = run_name
        self.voxel_spacing = voxel_spacing
