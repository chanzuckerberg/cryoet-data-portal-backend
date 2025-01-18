from importers.run import RunImporter


def test_runs_exist(runs: RunImporter):
    assert len(runs) != 0
