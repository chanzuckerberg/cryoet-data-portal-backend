from typing import Any, Callable

import pytest as pytest
import sqlalchemy as sa
from database import models
from db_import.tests.populate_db import (
    RUN1_ID,
    populate_run,
    write_data,
)
from platformics.database.models import Base
from sqlalchemy.orm import Session


@pytest.fixture
def expected_entries(http_prefix: str) -> list[dict[str, Any]]:
    return [
        {
            "s3_mdoc_path": "s3://test-public-bucket/30001/RUN1/Frames/foo.mdoc",
            "https_mdoc_path": f"{http_prefix}/30001/RUN1/Frames/foo.mdoc",
        },
    ]


@write_data
def populate_existing_mdoc(session: sa.orm.Session) -> None:
    populate_run(session)
    stale_frame = models.FrameAcquisitionFile(
        run_id=RUN1_ID,
        s3_mdoc_path="STALE_S3_PATH",
        https_mdoc_path="STALE_HTTP_PATH",
    )
    session.add(stale_frame)
    existing_mdoc = models.FrameAcquisitionFile(
        id=333,
        run_id=RUN1_ID,
        s3_mdoc_path="s3://test-public-bucket/30001/RUN1/Frames/foo.mdoc",
        https_mdoc_path="https://foo.com/",
    )
    session.add(existing_mdoc)


# Tests addition of new frames, and updating entries already existing in db
def test_import_frame_acquisition_files(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_entries: list[dict[str, Any]],
) -> None:
    populate_existing_mdoc(sync_db_session)
    sync_db_session.commit()
    actual = verify_dataset_import(import_frame_acquisition_files=True)
    expected_iter = iter(expected_entries)
    for run in [run for run in actual.runs if run.name == "RUN1"]:
        assert len(run.frame_acquisition_files) == 1
        assert run.frame_acquisition_files[0].id == 333
        for frame_acquisition_file in run.frame_acquisition_files:
            expected = next(expected_iter)
            if "run_id" not in expected:
                expected["run_id"] = run.id
            verify_model(frame_acquisition_file, expected)
