from typing import Dict

import allure
import pytest


@pytest.mark.run
@pytest.mark.parametrize("run_name", pytest.run_name, scope="session")
class TestRun:
    @allure.title("Run: sanity check run metadata.")
    def test_metadata(self, run_name: str, run_metadata: Dict):
        assert run_metadata["run_name"] == run_name
        if "last_updated_at" in run_metadata:
            assert isinstance(run_metadata["last_updated_at"], int)
