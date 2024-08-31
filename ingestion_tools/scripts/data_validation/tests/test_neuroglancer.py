from typing import Dict

import allure
import pytest
from tests.test_deposition import HelperTestDeposition

from common.fs import FileSystemApi


@pytest.mark.tomogram
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestNeuroglancer:
    @allure.title("Neuroglancer: sanity check neuroglancer config file.")
    def test_metadata(self, neuroglancer_config: Dict):
        assert len(neuroglancer_config) > 0

    @allure.title("Neuroglancer: valid corresponding deposition metadata.")
    def test_deposition_id(self, neuroglancer_config: Dict, bucket: str, filesystem: FileSystemApi):
        HelperTestDeposition.check_deposition_metadata(neuroglancer_config["deposition_id"], bucket, filesystem)
