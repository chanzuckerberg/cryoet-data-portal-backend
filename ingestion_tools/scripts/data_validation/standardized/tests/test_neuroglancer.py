from typing import Dict, List

import allure
import pytest


@pytest.mark.tomogram
@pytest.mark.parametrize("dataset, run_name, voxel_spacing", pytest.cryoet.dataset_run_spacing_combinations, scope="session")
class TestNeuroglancer:
    @allure.title("Neuroglancer: sanity check neuroglancer config file.")
    def test_metadata(self, neuroglancer_configs: List[Dict]):
        for neuroglancer_config in neuroglancer_configs:
            assert "layers" in neuroglancer_config and len(neuroglancer_config["layers"]) > 0
