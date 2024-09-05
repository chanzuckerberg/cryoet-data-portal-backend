from typing import Dict

import pytest


@pytest.mark.run
@pytest.mark.parametrize("run_name", pytest.run_name, scope="session")
class TestRun:
    def test_run_metadata(self, run_name: str, run_metadata: Dict):
        """A run metadata sanity check."""
        assert len(run_metadata) == 1
        assert run_metadata["run_name"] == run_name
