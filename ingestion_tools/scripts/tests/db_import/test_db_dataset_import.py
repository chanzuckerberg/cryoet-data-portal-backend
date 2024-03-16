import datetime
from typing import Any, Callable

import pytest
import common.db_models as models


DATASET_ID = 30001


def populate_dataset_author_table() -> None:
    models.DatasetAuthor(id=1, dataset_id=10000, name="Julia Child", author_list_order=1).save(force_insert=True)
    models.DatasetAuthor(id=2, dataset_id=DATASET_ID, name="Stale Author", author_list_order=1).save(force_insert=True)
    models.DatasetAuthor(id=3, dataset_id=DATASET_ID, name="Virginia Woolf", author_list_order=3).save(
        force_insert=True
    )


def populate_dataset_funding_table() -> None:
    models.DatasetFunding(id=1, dataset_id=10000, funding_agency_name="Grant Provider 1").save(force_insert=True)
    models.DatasetFunding(id=2, dataset_id=DATASET_ID, funding_agency_name="Grant Provider 1", grant_id="foo").save(
        force_insert=True
    )
    # TODO: Add functionality to remove stale data
    # models.DatasetFunding(id=3, dataset_id=DATASET_ID, funding_agency_name="Grant Provider 2").save(force_insert=True)
    models.DatasetFunding(id=3, dataset_id=10000, funding_agency_name="Grant Provider 2").save(force_insert=True)


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
    assert len(actual.authors) == 0
    assert len(actual.funding_sources) == 0


# Tests update of dataset existing in database
def test_import_dataset_update(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
) -> None:
    today = datetime.date.today()
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
    assert len(actual.authors) == 0
    assert len(actual.funding_sources) == 0


# Tests addition of new authors, updating entries already existing in db, and removing stale authors
def test_import_dataset_and_dataset_authors(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    dataset_30001_authors_expected: list[dict[str, Any]],
) -> None:
    populate_dataset_author_table()
    actual = verify_dataset_import(["--import-dataset-authors"])
    assert len(actual.authors) == len(dataset_30001_authors_expected)
    assert len(actual.funding_sources) == 0
    actual_authors = [author for author in actual.authors.order_by(models.DatasetAuthor.author_list_order)]
    for i, author in enumerate(actual_authors):
        verify_model(author, dataset_30001_authors_expected[i])


# Tests addition of new funding sources, and updating entries already existing in db
def test_import_dataset_and_dataset_funding(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    dataset_30001_funding_expected: list[dict[str, Any]],
) -> None:
    populate_dataset_funding_table()
    actual = verify_dataset_import(["--import-dataset-funding"])
    assert len(actual.authors) == 0
    assert len(actual.funding_sources) == len(dataset_30001_funding_expected)
    actual_funding_sources = [author for author in actual.funding_sources]
    for i, funding_sources in enumerate(actual_funding_sources):
        verify_model(funding_sources, dataset_30001_funding_expected[i])
