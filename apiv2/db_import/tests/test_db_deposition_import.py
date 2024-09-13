from datetime import date
from typing import Any, Callable

import pytest
from database import models
from db_import.tests.populate_db import (
    DEPOSITION_AUTHOR_ID,
    DEPOSITION_ID1,
    DEPOSITION_ID2,
    populate_deposition,
    populate_deposition_authors,
    stale_deposition_author,
    stale_deposition_metadata,
)
from sqlalchemy.orm import Session

from platformics.database.models import Base


@pytest.fixture
def expected_deposition1(http_prefix: str) -> dict[str, Any]:
    return {
        "id": DEPOSITION_ID1,
        "deposition_title": "ipsum dolor sit amet",
        "deposition_description": (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et"
            " dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip"
            " ex ea commodo consequat."
        ),
        "deposition_date": date(2023, 5, 2),
        "release_date": date(2023, 6, 1),
        "last_modified_date": date(2023, 4, 2),
        "related_database_entries": None,
        "publications": None,
    }


@pytest.fixture
def expected_dep1_authors() -> list[dict[str, Any]]:
    return [
        {
            "id": DEPOSITION_AUTHOR_ID,
            "deposition_id": DEPOSITION_ID1,
            "orcid": "0000-0000-0000-0001",
            "name": "Author 1",
            "primary_author_status": True,
            "author_list_order": 1,
        },
        {
            "deposition_id": DEPOSITION_ID1,
            "orcid": "0000-0000-0000-0002",
            "name": "Author 2",
            "corresponding_author_status": True,
            "author_list_order": 2,
        },
    ]


@pytest.fixture
def expected_deposition2(http_prefix: str) -> dict[str, Any]:
    return {
        "id": DEPOSITION_ID2,
        "deposition_title": "Deposition 2",
        "deposition_description": "A really awesome deposition",
        "deposition_date": date(2023, 4, 2),
        "release_date": date(2024, 6, 1),
        "last_modified_date": date(2023, 9, 2),
        "related_database_entries": "EMPIAR-1000, EMDB-1001",
        "publications": "doi:10.1000/1234",
    }


@pytest.fixture
def expected_dep2_authors() -> list[dict[str, Any]]:
    return [
        {
            "deposition_id": DEPOSITION_ID2,
            "orcid": "0000-0000-0000-1000",
            "name": "Author 3",
            "primary_author_status": True,
            "author_list_order": 1,
        },
        {
            "deposition_id": DEPOSITION_ID2,
            "orcid": "0000-0000-0000-0005",
            "name": "Author 4",
            "author_list_order": 2,
        },
        {
            "deposition_id": DEPOSITION_ID2,
            "orcid": "0000-0000-0000-0002",
            "name": "Author 2",
            "corresponding_author_status": True,
            "author_list_order": 3,
        },
    ]


# Tests addition of new deposition to database
def test_import_deposition_new(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_deposition2: dict[str, Any],
    expected_dep2_authors: list[dict[str, Any]],
) -> None:
    verify_dataset_import(import_depositions=True, deposition_id=[DEPOSITION_ID2])
    actual = sync_db_session.get(models.Deposition, DEPOSITION_ID2)
    verify_model(actual, expected_deposition2)
    assert len(actual.authors) == 3
    actual_authors = sorted(actual.authors, key=lambda x: x.author_list_order)
    for i, author in enumerate(actual_authors):
        verify_model(author, expected_dep2_authors[i])


# Tests update of deposition existing in database, and addition of new authors, updating entries already existing in
# db, and removing stale authors
def test_import_deposition_update(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
    expected_deposition1: dict[str, Any],
    expected_dep1_authors: list[dict[str, Any]],
) -> None:
    populate_deposition(sync_db_session)
    populate_deposition_authors(sync_db_session)
    sync_db_session.commit()
    verify_dataset_import(import_depositions=True, deposition_id=[DEPOSITION_ID1])
    actual = sync_db_session.get(models.Deposition, DEPOSITION_ID1)
    verify_model(actual, expected_deposition1)
    assert len(actual.authors) == 2
    actual_authors = sorted(actual.authors, key=lambda x: x.author_list_order)
    for i, author in enumerate(actual_authors):
        verify_model(author, expected_dep1_authors[i])


# Tests importing related entity doesn't update the deposition when no import specified
def test_import_deposition_no_update(
    sync_db_session: Session,
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[Base, dict[str, Any]], None],
) -> None:
    populate_deposition(sync_db_session)
    populate_deposition_authors(sync_db_session)
    sync_db_session.commit()
    verify_dataset_import()
    actual = sync_db_session.get(models.Deposition, DEPOSITION_ID1)
    verify_model(actual, stale_deposition_metadata())
    assert len(actual.authors) == 1
    actual_authors = sorted(actual.authors, key=lambda x: x.author_list_order)
    verify_model(actual_authors[0], stale_deposition_author())
