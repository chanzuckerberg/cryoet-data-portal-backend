from typing import Any, Callable

import pytest as pytest
from database import models
from db_import.tests.populate_db import (
    DATASET_ID,
    RUN1_ID,
    RUN4_ID,
    populate_run,
    populate_stale_run,
    populate_stale_tiltseries,
)
from sqlalchemy.orm import Session

from platformics.database.models import Base


@pytest.fixture
def expected_runs(http_prefix: str) -> list[dict[str, Any]]:
    return [
        {
            "id": RUN1_ID,
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
        {
            "id": RUN4_ID,
            "dataset_id": DATASET_ID,
            "name": "RUN4",
            "s3_prefix": f"s3://test-public-bucket/{DATASET_ID}/RUN4/",
            "https_prefix": f"{http_prefix}/{DATASET_ID}/RUN4/",
        },
    ]


# Tests addition of new runs, and updating entries already existing in db
def test_import_run(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_runs: list[dict[str, Any]],
) -> None:
    populate_run(sync_db_session)
    sync_db_session.commit()
    actual = verify_dataset_import(import_runs=True)
    actual_runs = sorted(actual.runs, key=lambda x: x.name)
    assert len(expected_runs) == len(actual_runs)
    for i, run in enumerate(actual_runs):
        verify_model(run, expected_runs[i])


# Tests deletion of stale runs existing in db
def test_import_run_stale_deletion(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_runs: list[dict[str, Any]],
) -> None:
    populate_run(sync_db_session)
    populate_stale_run(sync_db_session)
    populate_stale_tiltseries(sync_db_session)
    sync_db_session.commit()
    actual = verify_dataset_import(import_runs=True)
    actual_runs = sorted(actual.runs, key=lambda x: x.name)
    assert len(expected_runs) == len(actual_runs)
    for i, run in enumerate(actual_runs):
        verify_model(run, expected_runs[i])
