import pytest
from importers.run import RunImporter


@pytest.fixture(scope="module")
def runs() -> list[RunImporter]:
    return pytest.cryoet.runs

def test_runs_exist(runs):
    assert len(runs) != 0
