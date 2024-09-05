from typing import Dict

import allure
import pytest


@pytest.mark.tomogram
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestNeuroglancer:
    @allure.title("Neuroglancer: sanity check neuroglancer config file.")
    def test_metadata(self, neuroglancer_config: Dict):
        assert "layers" in neuroglancer_config and len(neuroglancer_config["layers"]) > 0
