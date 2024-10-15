from typing import Any, Callable

import pytest as pytest
import sqlalchemy as sa
from database import models
from db_import.tests.populate_db import (
    DEPOSITION_ID1,
    RUN1_ID,
    populate_run,
    write_data,
)
from sqlalchemy.orm import Session

from platformics.database.models import Base


@pytest.fixture
def expected_frames(http_prefix: str) -> list[dict[str, Any]]:
    return [
        {
            "s3_frame_path": "s3://test-public-bucket/30001/RUN1/Frames/frame1",
            "https_frame_path": "https://foo.com/30001/RUN1/Frames/frame1",
        },
        {
            "s3_frame_path": "s3://test-public-bucket/30001/RUN1/Frames/frame2",
            "https_frame_path": "https://foo.com/30001/RUN1/Frames/frame2",
        },
    ]


@write_data
def populate_existing_frames(session: sa.orm.Session) -> models.Frame:
    populate_run(session)
    stale_frame = models.Frame(
        run_id=RUN1_ID, deposition_id=DEPOSITION_ID1, https_frame_path="STALE_FRAME", s3_frame_path="STALE_FRAME",
    )
    session.add(stale_frame)
    return models.Frame(
        id=333,
        run_id=RUN1_ID,
        deposition_id=DEPOSITION_ID1,
        s3_frame_path="s3://test-public-bucket/30001/RUN1/Frames/frame1",
        https_frame_path="https://foo.com/30001/RUN1/Frames/frame1",
    )


# Tests addition of new frames, and updating entries already existing in db
def test_import_frames(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_frames: list[dict[str, Any]],
) -> None:
    populate_existing_frames(sync_db_session)
    sync_db_session.commit()
    actual = verify_dataset_import(import_frames=True)
    expected_iter = iter(expected_frames)
    for run in [run for run in actual.runs if run.name == "RUN1"]:
        assert len(run.frames) == 2
        assert run.frames[0].id == 333
        for frame in run.frames:
            expected = next(expected_iter)
            if "run_id" not in expected:
                expected["run_id"] = run.id
            verify_model(frame, expected)
