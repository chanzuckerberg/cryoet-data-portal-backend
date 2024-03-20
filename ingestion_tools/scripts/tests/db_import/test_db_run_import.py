from typing import Any, Callable

import pytest as pytest
from tests.db_import.populate_db import DATASET_ID, RUN_ID, populate_runs_table

import common.db_models as models


@pytest.fixture
def expected_runs(http_prefix: str) -> list[dict[str, Any]]:
    return [
        {
            "id": RUN_ID,
            "dataset_id": DATASET_ID,
            "name": "RUN1",
            "s3_prefix": f"s3://test-public-bucket/{DATASET_ID}/RUN1/",
            "https_prefix": f"{http_prefix}/{DATASET_ID}/RUN1/",
        },
        {
            "dataset_id": DATASET_ID,
            "name": "RUN2",
            "s3_prefix": f"s3://test-public-bucket/{DATASET_ID}/RUN2/",
            "https_prefix": f"{http_prefix}/{DATASET_ID}/RUN2/",
        },
        {
            "dataset_id": DATASET_ID,
            "name": "RUN3",
            "s3_prefix": f"s3://test-public-bucket/{DATASET_ID}/RUN3/",
            "https_prefix": f"{http_prefix}/{DATASET_ID}/RUN3/",
        },
    ]


# Tests addition of new runs, and updating entries already existing in db
def test_import_run(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    expected_runs: list[dict[str, Any]],
) -> None:
    populate_runs_table()
    actual = verify_dataset_import(["--import-runs"])
    actual_runs = list(actual.runs)
    for i, run in enumerate(actual_runs):
        verify_model(run, expected_runs[i])
