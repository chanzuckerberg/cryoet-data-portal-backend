from typing import Any, Callable

import pytest
from database import models
from db_import.tests.populate_db import (
    DATASET_AUTHOR_ID,
    DATASET_FUNDING_ID,
    DATASET_ID,
    populate_dataset,
    populate_dataset_authors,
    populate_dataset_funding,
    populate_stale_dataset_authors,
    populate_stale_dataset_funding,
)
from sqlalchemy.orm import Session

from platformics.database.models import Base


@pytest.fixture
def expected_authors() -> list[dict[str, Any]]:
    return [
        {
            "dataset_id": DATASET_ID,
            "name": "Jane Eyre",
            "corresponding_author_status": False,
            "primary_author_status": True,
            "author_list_order": 1,
        },
        {
            "id": DATASET_AUTHOR_ID,
            "dataset_id": DATASET_ID,
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
            "dataset_id": DATASET_ID,
            "orcid": "9876-0000-0000-0000",
            "name": "Julia Child",
            "corresponding_author_status": True,
            "primary_author_status": False,
            "author_list_order": 3,
        },
    ]


@pytest.fixture
def expected_funding_sources() -> list[dict[str, Any]]:
    return [
        {
            "id": DATASET_FUNDING_ID,
            "dataset_id": DATASET_ID,
            "funding_agency_name": "Grant Provider 1",
            "grant_id": "1234",
        },
        {
            "dataset_id": DATASET_ID,
            "funding_agency_name": "Grant Provider 1",
            "grant_id": "5678",
        },
        {
            "dataset_id": DATASET_ID,
            "funding_agency_name": "Test Agency 1",
            "grant_id": "56789",
        },
        {
            "dataset_id": DATASET_ID,
            "funding_agency_name": "Test Agency 2",
        },
    ]


# Tests addition of new dataset to database
def test_import_dataset_new(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
) -> None:
    actual = verify_dataset_import()
    assert len(actual.authors) == 0
    assert len(actual.funding_sources) == 0


# Tests update of dataset existing in database
def test_import_dataset_update(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
) -> None:
    populate_dataset(sync_db_session)
    populate_dataset_authors(sync_db_session)
    populate_dataset_funding(sync_db_session)
    sync_db_session.commit()
    actual = verify_dataset_import()
    assert len(actual.authors) == 1
    assert len(actual.funding_sources) == 1


def test_import_dataset_and_dataset_authors(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_authors: list[dict[str, Any]],
) -> None:
    """Tests addition of new authors, updating entries already existing in db, and removing stale authors"""
    populate_dataset(sync_db_session)
    populate_dataset_authors(sync_db_session)
    populate_dataset_funding(sync_db_session)
    sync_db_session.commit()
    actual = verify_dataset_import(import_dataset_authors=True)
    assert len(actual.authors) == len(expected_authors)
    assert len(actual.funding_sources) == 1
    actual_authors = sorted(actual.authors, key=lambda x: x.author_list_order)
    for i, author in enumerate(actual_authors):
        verify_model(author, expected_authors[i])


def test_import_dataset_and_dataset_funding(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_funding_sources: list[dict[str, Any]],
) -> None:
    """Tests addition of new funding sources, and updating entries already existing in db"""
    populate_dataset(sync_db_session)
    populate_dataset_authors(sync_db_session)
    populate_dataset_funding(sync_db_session)
    sync_db_session.commit()
    actual = verify_dataset_import(import_dataset_funding=True)
    assert len(actual.authors) == 1
    assert len(actual.funding_sources) == len(expected_funding_sources)
    actual_funding_sources = sorted(actual.funding_sources, key=lambda x: x.funding_agency_name)
    for i, funding_sources in enumerate(actual_funding_sources):
        verify_model(funding_sources, expected_funding_sources[i])


def test_import_dataset_funding_and_authors_remove_stale(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_authors: list[dict[str, Any]],
    expected_funding_sources: list[dict[str, Any]],
) -> None:
    populate_dataset(sync_db_session)
    populate_dataset_authors(sync_db_session)
    populate_stale_dataset_authors(sync_db_session)
    populate_dataset_funding(sync_db_session)
    populate_stale_dataset_funding(sync_db_session)
    sync_db_session.commit()
    actual = verify_dataset_import(import_dataset_authors=True, import_dataset_funding=True)
    assert len(actual.authors) == len(expected_authors)
    actual_authors = sorted(actual.authors, key=lambda x: x.author_list_order)
    for i, author in enumerate(actual_authors):
        verify_model(author, expected_authors[i])
    assert len(actual.funding_sources) == len(expected_funding_sources)
    actual_funding_sources = sorted(actual.funding_sources, key=lambda x: x.funding_agency_name)
    for i, funding_sources in enumerate(actual_funding_sources):
        verify_model(funding_sources, expected_funding_sources[i])
