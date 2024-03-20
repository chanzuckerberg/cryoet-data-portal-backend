import datetime
from typing import Any, Callable

import pytest

import common.db_models as models

DATASET_ID = 30001


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
        },
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
        },
    ]


# Tests addition of new dataset to database
def test_import_dataset_new(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
) -> None:
    actual = verify_dataset_import([])
    assert len(actual.authors) == 2
    assert len(actual.funding_sources) == 1


# Tests update of dataset existing in database
def test_import_dataset_update(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
) -> None:
    today = datetime.datetime.now().date()
    models.Dataset(
        id=DATASET_ID,
        title="foo",
        description="bar",
        deposition_date=today,
        release_date=today,
        last_modified_date=today,
        sample_type="test",
        s3_prefix="s3://invalid_bucket/",
        https_prefix="https://invalid-site.com/1234",
    ).save(force_insert=True)
    actual = verify_dataset_import([])
    assert len(actual.authors) == 2
    assert len(actual.funding_sources) == 1


# Tests addition of new authors, updating entries already existing in db, and removing stale authors
def test_import_dataset_and_dataset_authors(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    dataset_30001_authors_expected: list[dict[str, Any]],
) -> None:
    actual = verify_dataset_import(["--import-dataset-authors"])
    assert len(actual.authors) == len(dataset_30001_authors_expected)
    assert len(actual.funding_sources) == 1
    actual_authors = list(actual.authors.order_by(models.DatasetAuthor.author_list_order))
    for i, author in enumerate(actual_authors):
        verify_model(author, dataset_30001_authors_expected[i])


# Tests addition of new funding sources, and updating entries already existing in db
def test_import_dataset_and_dataset_funding(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    dataset_30001_funding_expected: list[dict[str, Any]],
) -> None:
    actual = verify_dataset_import(["--import-dataset-funding"])
    assert len(actual.authors) == 2
    assert len(actual.funding_sources) == len(dataset_30001_funding_expected)
    actual_funding_sources = list(actual.funding_sources)
    for i, funding_sources in enumerate(actual_funding_sources):
        verify_model(funding_sources, dataset_30001_funding_expected[i])
