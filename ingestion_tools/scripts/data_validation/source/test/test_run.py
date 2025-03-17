import pytest


def test_runs_exist():
    assert len(pytest.cryoet.runs) != 0, "No runs found"
