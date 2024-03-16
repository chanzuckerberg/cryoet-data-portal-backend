from typing import Callable, Any

import pytest as pytest

import common.db_models as models


@pytest.fixture
def dataset_30001_runs_expected(http_prefix: str) -> list[dict[str, Any]]:
    return [
        {
            "id": 2,
            "dataset_id": 30001,
            "name": "RUN1",
            "s3_prefix": "s3://test-public-bucket/30001/RUN1/",
            "https_prefix": f"{http_prefix}/30001/RUN1/",
        },
        {
            "id": 3,
            "dataset_id": 30001,
            "name": "RUN2",
            "s3_prefix": "s3://test-public-bucket/30001/RUN2/",
            "https_prefix": f"{http_prefix}/30001/RUN2/",
        },
    ]


# Tests addition of new runs, and updating entries already existing in db
def test_import_run(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    dataset_30001_runs_expected: list[dict[str, Any]],
) -> None:
    models.Run(
        id=2,
        dataset_id=30001,
        name="RUN1",
        s3_prefix="s3://test-public-bucket/1000/RUN1",
        https_prefix="http://test.com/10000/RUN1",
    ).save(force_insert=True)
    actual = verify_dataset_import(["--import-runs"])
    actual_runs = [run for run in actual.runs]
    for i, run in enumerate(actual_runs):
        verify_model(run, dataset_30001_runs_expected[i])
