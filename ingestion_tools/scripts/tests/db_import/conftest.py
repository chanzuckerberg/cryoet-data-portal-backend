from datetime import date
from typing import Any, Callable, Generator

import pytest
from click.testing import CliRunner
from db_import import load
from mypy_boto3_s3 import S3Client
from peewee import SqliteDatabase
from tests.db_import.populate_db import populate_all_tables

from common.db_models import BaseModel, Dataset, DatasetAuthor, DatasetFunding, Run, TiltSeries, TomogramVoxelSpacing


@pytest.fixture
def default_inputs(endpoint_url: str, http_prefix: str) -> list[str]:
    # Setting this to empty as we initialize a test DB in mock_db
    postgres_url = ""
    return ["test-public-bucket", http_prefix, postgres_url, "--endpoint-url", endpoint_url]


@pytest.fixture
def mock_db() -> [list[BaseModel], Generator[SqliteDatabase, Any, None]]:
    models = [Dataset, DatasetAuthor, DatasetFunding, Run, TiltSeries, TomogramVoxelSpacing]
    mock_db = SqliteDatabase(":memory:")
    mock_db.bind(models, bind_refs=False, bind_backrefs=False)
    mock_db.connect()
    mock_db.create_tables(models)
    populate_all_tables()
    yield mock_db
    mock_db.drop_tables(models)
    mock_db.close()


@pytest.fixture
def verify_model():
    def _verify_model(actual: BaseModel, expected_values: dict[str, Any]):
        for key, value in actual.__data__.items():
            expected = expected_values.get(key)
            assert value == expected, f"Unexpected value for {key} actual={value} expected={expected}"

    return _verify_model


@pytest.fixture
def verify_dataset_import(
    mock_db: Generator[SqliteDatabase, Any, None],
    s3_client: S3Client,
    default_inputs: list[str],
    verify_model: Callable[[BaseModel, dict[str, Any]], None],
    dataset_30001_expected: dict[str, Any],
) -> Callable[[list[str]], Dataset]:
    def _verify(additional_inputs: list[str]) -> Dataset:
        input_args = default_inputs + ["--s3_prefix", "30001"] + additional_inputs
        CliRunner().invoke(load, input_args)
        actual = Dataset.get(id=30001)
        verify_model(actual, dataset_30001_expected)
        return actual

    return _verify


@pytest.fixture
def dataset_30001_expected(http_prefix: str) -> dict[str, Any]:
    return {
        "id": 30001,
        "title": "Lorem ipsum dolor",
        "description": (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et"
            " dolore magna aliqua."
        ),
        "deposition_date": date(2023, 4, 1),
        "release_date": date(2023, 6, 2),
        "last_modified_date": date(2023, 8, 5),
        "s3_prefix": "s3://test-public-bucket/30001/",
        "https_prefix": f"{http_prefix}/30001/",
        "dataset_publications": "test-publication-data",
        "dataset_citations": "10.1101/2024.01.12.111111",
        "related_database_entries": "TEST-1243435",
        "sample_preparation": "method1: value1, method2: value3",
        "grid_preparation": "method3: value8, method6: value4",
        "dataset_identifier": 30001,
        "sample_type": "organism",
        "cell_component_id": "GO:123435",
        "cell_component_name": "tail",
        "cell_strain_id": "999999",
        "cell_strain_name": "test value",
        "cell_type_id": "4321",
        "cell_name": "foo",
        "organism_taxid": "1111",
        "organism_name": "Foo Bar",
        "tissue_id": "1234",
        "tissue_name": "test-tissue1",
        "key_photo_url": f"{http_prefix}/30001/KeyPhoto/snapshot.png",
        "key_photo_thumbnail_url": f"{http_prefix}/30001/KeyPhoto/thumbnail.png",
    }
