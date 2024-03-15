from datetime import date
from typing import Any, Generator
import pytest
from peewee import SqliteDatabase

from common.db_models import BaseModel, Dataset, DatasetAuthor, DatasetFunding


@pytest.fixture
def default_inputs(endpoint_url: str, http_prefix: str) -> list[str]:
    # Setting this to empty as we initialize a test DB in mock_db
    postgres_url = ""
    return ["test-public-bucket", http_prefix, postgres_url, "--endpoint-url", endpoint_url]


@pytest.fixture
def mock_db() -> [list[BaseModel], Generator[SqliteDatabase, Any, None]]:
    MODELS = [Dataset, DatasetAuthor, DatasetFunding]
    mock_db = SqliteDatabase(":memory:")
    mock_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    mock_db.connect()
    mock_db.create_tables(MODELS)
    yield mock_db
    mock_db.drop_tables(MODELS)
    mock_db.close()


@pytest.fixture
def verify_model():
    def _verify_model(actual: BaseModel, expected_values: dict[str, Any]):
        for key, value in actual.__data__.items():
            expected = expected_values.get(key)
            assert value == expected, f"Unexpected value for {key} actual={value} expected={expected}"
    return _verify_model


@pytest.fixture
def dataset_30001_expected(http_prefix: str) -> dict[str, Any]:
    return {
        "id": 30001,
        "title": "Lorem ipsum dolor",
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
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
        "key_photo_thumbnail_url": f"{http_prefix}/30001/KeyPhoto/thumbnail.png"
    }


@pytest.fixture
def dataset_30001_authors_expected() -> list[dict[str, Any]]:
    return [
        {
            "id": 4,
            "dataset_id": 30001,
            "name": "Jane Eyre",
            "corresponding_author_status": False,
            "primary_author_status": True,
            "author_list_order": 1,
        },
        {
            "id": 3,
            "dataset_id": 30001,
            "orcid": "0000-0000-1234-0000",
            "name": "Virginia Woolf",
            "corresponding_author_status": False,
            "primary_author_status": False,
            "email": "vwoolf@dall.way",
            "affiliation_name": "Bloomsbury",
            "affiliation_address": "London, UK",
            "affiliation_identifier": "1234343",
            "author_list_order": 2,
        },
        {
            "id": 5,
            "dataset_id": 30001,
            "orcid": "9876-0000-0000-0000",
            "name": "Julia Child",
            "corresponding_author_status": True,
            "primary_author_status": False,
            "author_list_order": 3,
        }
    ]


@pytest.fixture
def dataset_30001_funding_expected() -> list[dict[str, Any]]:
    return [
        {
            "id": 2,
            "dataset_id": 30001,
            "funding_agency_name": "Grant Provider 1",
            "grant_id": "1234",
        },
        {
            "id": 4,
            "dataset_id": 30001,
            "funding_agency_name": "Test Agency 1",
            "grant_id": "56789",
        },
        {
            "id": 5,
            "dataset_id": 30001,
            "funding_agency_name": "Test Agency 2",
        }
    ]

