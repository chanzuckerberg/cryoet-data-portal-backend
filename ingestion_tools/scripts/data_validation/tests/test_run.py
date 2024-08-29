from typing import Dict

import allure
import pytest


@pytest.mark.run
@pytest.mark.parametrize("run_name", pytest.run_name, scope="session")
class TestRun:
    @allure.title("Sanity check run metadata.")
    def test_run_metadata(self, run_name: str, run_metadata: Dict):
        assert len(run_metadata) == 1
        assert run_metadata["run_name"] == run_name
