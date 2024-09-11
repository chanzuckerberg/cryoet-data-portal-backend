import os
from datetime import date
from typing import Any, Callable, Generator

import pytest
from click.testing import CliRunner
from db_import import load
from mypy_boto3_s3 import S3Client
from peewee import PostgresqlDatabase, SqliteDatabase
from tests.db_import.populate_db import DATASET_ID, clean_all_mock_data
from platformics.database.models import Base

from database.models import (
    Annotation,
    AnnotationAuthor,
    AnnotationFile,
    Dataset,
    DatasetAuthor,
    DatasetFunding,
    Deposition,
    DepositionAuthor,
    Run,
    Tiltseries,
    Tomogram,
    TomogramAuthor,
    TomogramVoxelSpacing,
)


@pytest.fixture
def db_connection() -> str:
    return os.getenv("DB_CONNECTION", "postgresql://postgres:postgres@db:5432/cryoet")


@pytest.fixture
def default_inputs(endpoint_url: str, http_prefix: str, db_connection: str) -> list[str]:
    return ["test-public-bucket", http_prefix, db_connection, "--endpoint-url", endpoint_url]


@pytest.fixture
def mock_db(db_connection: str) -> [list[Base], Generator[SqliteDatabase, Any, None]]:
    mock_db = PostgresqlDatabase(db_connection)
    mock_db.connect()
    models = [
        Dataset,
        DatasetAuthor,
        DatasetFunding,
        Deposition,
        DepositionAuthor,
        Run,
        Tiltseries,
        TomogramVoxelSpacing,
        Tomogram,
        TomogramAuthor,
        Annotation,
        AnnotationFile,
        AnnotationAuthor,
    ]
    mock_db.bind(models, bind_refs=False, bind_backrefs=False)
    clean_all_mock_data()
    yield mock_db
    mock_db.close()


@pytest.fixture
def verify_model():
    def _verify_model(actual_model: Base, expected_values: dict[str, Any]):
        actual_data = actual_model.__data__
        for key, expected in expected_values.items():
            actual = actual_data.get(key)
            assert actual == expected, f"Unexpected value for {key} actual={actual} expected={expected}"
        for key in actual_data.keys() - expected_values.keys():
            if "id" in key:
                continue
            actual = actual_data.get(key)
            assert actual is None, f"Unexpected value for {key} actual={actual} expected=None"

    return _verify_model


@pytest.fixture
def verify_dataset_import(
    mock_db: Generator[SqliteDatabase, Any, None],
    s3_client: S3Client,
    default_inputs: list[str],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_dataset: dict[str, Any],
) -> Callable[[list[str]], Dataset]:
    def _verify(additional_inputs: list[str]) -> Dataset:
        input_args = default_inputs + ["--s3-prefix", str(DATASET_ID)] + additional_inputs
        result = CliRunner().invoke(load, input_args)
        assert result.exit_code == 0, "Execution didn't complete successfully"
        actual = Dataset.get(id=DATASET_ID)
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
        "dataset_publications": "test-publication-data",
        "dataset_citations": "10.1101/2024.01.12.111111",
        "related_database_entries": "TEST-1243435",
        "sample_preparation": "method1: value1, method2: value3",
        "grid_preparation": "method3: value8, method6: value4",
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
        "key_photo_url": f"{http_prefix}/{DATASET_ID}/KeyPhoto/snapshot.png",
        "key_photo_thumbnail_url": f"{http_prefix}/{DATASET_ID}/KeyPhoto/thumbnail.png",
        "deposition_id": 300,
    }
