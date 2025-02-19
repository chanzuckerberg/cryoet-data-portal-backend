import datetime
import os
from datetime import date
from typing import Any, Callable, Generator

import boto3
import pytest
import sqlalchemy as sa
from botocore.client import Config
from database.models import (
    Dataset,
)
from db_import.importer import load_func
from db_import.tests.populate_db import DATASET_ID
from mypy_boto3_s3 import S3Client

from platformics.database.connect import SyncDB
from platformics.database.models import Base


@pytest.fixture
def http_prefix() -> str:
    return "https://foo.com"


def model_to_dict(sa_object: Base) -> dict[str, Any]:
    return {item.key: getattr(sa_object, item.key) for item in sa.inspect(sa_object).mapper.column_attrs}


@pytest.fixture
def default_inputs(aws_endpoint_url: str, http_prefix: str, test_db_uri: str) -> dict[str, Any]:
    return {
        "s3_bucket": "test-public-bucket",
        "https_prefix": http_prefix,
        "postgres_url": f"postgresql+psycopg://{test_db_uri}",
        "endpoint_url": aws_endpoint_url,
    }


@pytest.fixture
def aws_endpoint_url() -> str:
    return os.getenv("BOTO_ENDPOINT_URL", "http://motoserver:5566")


@pytest.fixture
def s3_client(aws_endpoint_url: str) -> S3Client:
    return boto3.client(
        "s3",
        endpoint_url=aws_endpoint_url,
        config=Config(signature_version="s3v4"),
    )


@pytest.fixture
def sync_db_session(sync_db: SyncDB) -> Generator[sa.orm.Session, None, None]:
    with sync_db.session() as session:
        yield session


@pytest.fixture
def verify_model():
    def _verify_model(actual_model: Base, expected_values: dict[str, Any]):
        actual_data = model_to_dict(actual_model)
        for key, expected in expected_values.items():
            actual = actual_data.get(key)
            if isinstance(actual, datetime.datetime):
                expected = datetime.datetime(expected.year, expected.month, expected.day, tzinfo=datetime.UTC)
            assert actual == expected, f"Unexpected value for {key} actual={actual} expected={expected}"
        for key in actual_data.keys() - expected_values.keys():
            if "id" in key:
                continue
            actual = actual_data.get(key)
            assert actual is None, f"Unexpected value for {key} actual={actual} expected=None"

    return _verify_model


@pytest.fixture
def verify_dataset_import(
    s3_client: S3Client,
    sync_db_session: sa.orm.Session,
    default_inputs: dict[str, Any],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_dataset: dict[str, Any],
) -> Callable[[list[str]], Dataset]:
    def _verify(**inputs: dict[str, Any]) -> Dataset:
        inputs.update(default_inputs)
        inputs["s3_prefix"] = str(DATASET_ID)
        load_func(**inputs)
        actual = sync_db_session.scalars(sa.select(Dataset).where(Dataset.id == DATASET_ID)).one()
        verify_model(actual, expected_dataset)
        return actual

    return _verify


@pytest.fixture
def expected_dataset(http_prefix: str) -> dict[str, Any]:
    return {
        "id": DATASET_ID,
        "title": "Lorem ipsum dolor",
        "description": (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et"
            " dolore magna aliqua."
        ),
        "deposition_date": date(2023, 4, 1),
        "release_date": date(2023, 6, 2),
        "last_modified_date": date(2023, 8, 5),
        "s3_prefix": f"s3://test-public-bucket/{DATASET_ID}/",
        "https_prefix": f"{http_prefix}/{DATASET_ID}/",
        "related_database_entries": "TEST-1243435",
        "dataset_publications": "test-publication-data",
        "sample_preparation": "method1: value1, method2: value3",
        "grid_preparation": "method3: value8, method6: value4",
        "sample_type": "organism",
        "cell_component_id": "GO:123435",
        "cell_component_name": "tail",
        "cell_strain_id": "999999",
        "cell_strain_name": "test value",
        "cell_type_id": "4321",
        "cell_name": "foo",
        "organism_taxid": 1111,
        "organism_name": "Foo Bar",
        "tissue_id": "1234",
        "tissue_name": "test-tissue1",
        "other_setup": "Other Setup",
        "key_photo_url": f"{http_prefix}/{DATASET_ID}/KeyPhoto/snapshot.png",
        "key_photo_thumbnail_url": f"{http_prefix}/{DATASET_ID}/KeyPhoto/thumbnail.png",
        "deposition_id": 300,
        "file_size": 1379940.0,
    }
