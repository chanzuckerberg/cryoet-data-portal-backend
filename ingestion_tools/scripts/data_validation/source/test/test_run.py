import pytest


def test_runs_exist():
    assert len(pytest.cryoet.runs) != 0, "No runs found"


@pytest.mark.parametrize(
    "run",
    pytest.cryoet.runs,
    ids=[run.name for run in pytest.cryoet.runs],
    scope="session",
)
def test_at_most_one_tiltseries_per_run(run):
    matches = [ts.name for ts in pytest.cryoet.tiltseries if ts.get_run().name == run.name]
    assert len(matches) <= 1, (
        f"Run '{run.name}' resolves to {len(matches)} tiltseries ({matches}); each run may have at most one. "
        "Route run subgroups to a single tiltseries source with complementary parent_filters, "
        "or pick one stack (prefer the raw/unaligned form)."
    )
