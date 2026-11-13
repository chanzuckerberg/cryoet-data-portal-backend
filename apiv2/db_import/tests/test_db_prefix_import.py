"""Import the test dataset from a prefix inside the bucket, instead of from the bucket root."""

import re
from typing import Any, Generator

import pytest
import sqlalchemy as sa
from database import models
from db_import.importer import load_func
from db_import.tests.populate_db import DATASET_ID, DEPOSITION_ID1, DEPOSITION_ID2
from mypy_boto3_s3 import S3Client
from sqlalchemy.orm import Session

from platformics.database.models import Base

BUCKET = "test-public-bucket"
ROOT_PREFIX = "nested/prefix"
HTTP_PREFIX = f"https://foo.com/{ROOT_PREFIX}"
URL_COLUMN = re.compile(r"^(s3_|https_)|_url$")


@pytest.fixture
def prefixed_test_data(s3_client: S3Client) -> Generator[None, None, None]:
    """Copies the test dataset and depositions from the bucket root into ROOT_PREFIX."""
    keys = []
    paginator = s3_client.get_paginator("list_objects_v2")
    for source_prefix in (f"{DATASET_ID}/", "depositions_metadata/"):
        for page in paginator.paginate(Bucket=BUCKET, Prefix=source_prefix):
            for obj in page.get("Contents", []):
                key = f"{ROOT_PREFIX}/{obj['Key']}"
                s3_client.copy_object(Bucket=BUCKET, Key=key, CopySource={"Bucket": BUCKET, "Key": obj["Key"]})
                keys.append(key)
    assert keys, "no test data found in the bucket root, run test_infra/seed_moto.sh"
    yield
    for start in range(0, len(keys), 1000):
        s3_client.delete_objects(
            Bucket=BUCKET,
            Delete={"Objects": [{"Key": key} for key in keys[start : start + 1000]]},
        )


def url_values(session: Session) -> list[tuple[str, str, Any]]:
    """All values of the s3_*, https_* and *_url columns in the db, as (model, column, value)."""
    values = []
    for mapper in Base.registry.mappers:
        columns = [attr.key for attr in mapper.column_attrs if URL_COLUMN.search(attr.key)]
        if not columns:
            continue
        for row in session.scalars(sa.select(mapper.class_)).all():
            values.extend((mapper.class_.__name__, column, getattr(row, column)) for column in columns)
    return [item for item in values if item[2] is not None]


def test_import_from_prefix(
    prefixed_test_data: None,
    sync_db_session: Session,
    default_inputs: dict[str, Any],
) -> None:
    inputs = {
        **default_inputs,
        # The s3:// scheme and the trailing slash are optional.
        "s3_bucket": f"s3://{BUCKET}/{ROOT_PREFIX}/",
        "https_prefix": HTTP_PREFIX,
        "s3_prefix": str(DATASET_ID),
        "import_everything": True,
        "import_depositions": True,
        "deposition_id": [DEPOSITION_ID1, DEPOSITION_ID2],
    }
    load_func(**inputs)
    sync_db_session.expire_all()

    dataset = sync_db_session.get(models.Dataset, DATASET_ID)
    assert dataset.s3_prefix == f"s3://{BUCKET}/{ROOT_PREFIX}/{DATASET_ID}/"
    assert dataset.https_prefix == f"{HTTP_PREFIX}/{DATASET_ID}/"
    assert {run.name for run in dataset.runs} == {"RUN1", "RUN2", "RUN3", "RUN4"}
    for deposition_id in (DEPOSITION_ID1, DEPOSITION_ID2):
        assert sync_db_session.get(models.Deposition, deposition_id) is not None

    # Every url in the db points into the prefix, and none has it twice.
    values = url_values(sync_db_session)
    models_with_urls = {model for model, _, _ in values}
    for model in ("Dataset", "Deposition", "Run", "TomogramVoxelSpacing", "Tomogram", "Tiltseries", "Alignment"):
        assert model in models_with_urls
    for model in ("Annotation", "AnnotationFile", "Frame", "FrameAcquisitionFile", "GainFile"):
        assert model in models_with_urls
    for model, column, value in values:
        assert value.startswith(
            (f"s3://{BUCKET}/{ROOT_PREFIX}/", f"{HTTP_PREFIX}/"),
        ), f"{model}.{column} is not in the prefix: {value}"
        assert f"{ROOT_PREFIX}/{ROOT_PREFIX}" not in value, f"{model}.{column} has the prefix twice: {value}"

    # Links that are resolved by path. The annotation's alignment path has the bucket name in front of it.
    run1 = next(run for run in dataset.runs if run.name == "RUN1")
    alignment = sync_db_session.scalars(sa.select(models.Alignment).where(models.Alignment.run_id == run1.id)).one()
    assert alignment.tiltseries_id is not None
    tomograms = sync_db_session.scalars(sa.select(models.Tomogram).where(models.Tomogram.run_id == run1.id)).all()
    assert tomograms
    assert all(tomogram.alignment_id == alignment.id for tomogram in tomograms)
    annotation_files = sync_db_session.scalars(
        sa.select(models.AnnotationFile)
        .join(models.AnnotationFile.annotation_shape)
        .join(models.AnnotationShape.annotation)
        .where(models.Annotation.run_id == run1.id),
    ).all()
    assert annotation_files
    assert all(annotation_file.alignment_id == alignment.id for annotation_file in annotation_files)
