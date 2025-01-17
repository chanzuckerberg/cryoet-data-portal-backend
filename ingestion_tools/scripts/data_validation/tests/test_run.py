from typing import Dict

import allure
import pytest
from data_validation.tests.test_deposition import HelperTestDeposition

from common.fs import FileSystemApi


@pytest.mark.run
@pytest.mark.parametrize("dataset, run_name", pytest.cryoet.dataset_run_combinations, scope="session")
class TestRun:
    @allure.title("Run: sanity check run metadata.")
    def test_metadata(self, run_name: str, run_metadata: Dict):
        assert run_metadata["run_name"] == run_name
        if "last_updated_at" in run_metadata:
            assert isinstance(run_metadata["last_updated_at"], int)

    @allure.title("Run: valid corresponding deposition metadata.")
    def test_deposition_id(self, run_name, dataset_metadata: Dict, bucket: str, filesystem: FileSystemApi):
        # need run_name as parameter to prevent pytest error (expects run_name as a parametrized argument)
        del run_name
        # TODO: Change this to failing instead of skipping when all run_metadata.json has deposition id?
        if dataset_metadata["deposition_id"] is None:
            pytest.skip("No deposition_id for run found.")
        HelperTestDeposition.check_deposition_metadata(dataset_metadata["deposition_id"], bucket, filesystem)
