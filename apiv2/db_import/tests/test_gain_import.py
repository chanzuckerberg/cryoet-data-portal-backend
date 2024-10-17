from typing import Any, Callable

import pytest as pytest
import sqlalchemy as sa
from database import models
from db_import.tests.populate_db import (
    RUN1_ID,
    populate_run,
    write_data,
)
from sqlalchemy.orm import Session

from platformics.database.models import Base


@pytest.fixture
def expected_gains(http_prefix: str) -> list[dict[str, Any]]:
    return [
        {
            "s3_file_path": "s3://test-public-bucket/30001/RUN1/Frames/run1_gain.mrc",
            "https_file_path": "https://foo.com/30001/RUN1/Frames/run1_gain.mrc",
        },
        {
            "s3_file_path": "s3://test-public-bucket/30001/RUN1/Frames/run1a_gain.mrc",
            "https_file_path": "https://foo.com/30001/RUN1/Frames/run1a_gain.mrc",
        },
    ]


@write_data
def populate_existing_gains(session: sa.orm.Session) -> models.GainFile:
    populate_run(session)
    stale_frame = models.GainFile(run_id=RUN1_ID, https_file_path="STALE_GAIN", s3_file_path="STALE_FRAME")
    session.add(stale_frame)
    return models.GainFile(
        id=333,
        run_id=RUN1_ID,
        s3_file_path="s3://test-public-bucket/30001/RUN1/Frames/run1_gain.mrc",
        https_file_path="meep",
    )


# Tests addition of new gains, and updating entries already existing in db, and cleanup of old gains.
def test_import_gains(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_gains: list[dict[str, Any]],
) -> None:
    populate_existing_gains(sync_db_session)
    sync_db_session.commit()
    actual = verify_dataset_import(import_gains=True)
    expected_iter = iter(expected_gains)
    for run in [run for run in actual.runs if run.name == "RUN1"]:
        assert len(run.gain_files) == 2
        assert run.gain_files[0].id == 333
        for gain in run.gain_files:
            expected = next(expected_iter)
            if "run_id" not in expected:
                expected["run_id"] = run.id
            verify_model(gain, expected)
