from typing import Any, Callable

import pytest as pytest
from tests.db_import.populate_db import populate_run

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
        {
            "id": 4,
            "dataset_id": 30001,
            "name": "RUN3",
            "s3_prefix": "s3://test-public-bucket/30001/RUN3/",
            "https_prefix": f"{http_prefix}/30001/RUN3/",
        },
    ]


# Tests addition of new runs, and updating entries already existing in db
def test_import_run(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    dataset_30001_runs_expected: list[dict[str, Any]],
) -> None:
    populate_run()
    actual = verify_dataset_import(["--import-runs"])
    actual_runs = list(actual.runs)
    for i, run in enumerate(actual_runs):
        verify_model(run, dataset_30001_runs_expected[i])
