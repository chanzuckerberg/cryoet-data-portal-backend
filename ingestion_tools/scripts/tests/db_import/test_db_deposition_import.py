from datetime import date
from typing import Any, Callable

import pytest
from tests.db_import.populate_db import (
    DEPOSITION_AUTHOR_ID,
    DEPOSITION_ID1,
    DEPOSITION_ID2,
    populate_deposition,
    populate_deposition_authors,
    stale_deposition_author,
    stale_deposition_metadata,
)

import common.db_models as models


@pytest.fixture
def expected_deposition1(http_prefix: str) -> dict[str, Any]:
    return {
        "id": DEPOSITION_ID1,
        "title": "ipsum dolor sit amet",
        "description": (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et"
            " dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip"
            " ex ea commodo consequat."
        ),
        "deposition_date": date(2023, 5, 2),
        "release_date": date(2023, 6, 1),
        "last_modified_date": date(2023, 4, 2),
        "related_database_entries": None,
        "deposition_publications": None,
        "s3_prefix": f"s3://test-public-bucket/depositions_metadata/{DEPOSITION_ID1}/",
        "https_prefix": f"{http_prefix}/depositions_metadata/{DEPOSITION_ID1}/",
        "deposition_types": "annotation,dataset",
        "key_photo_url": f"{http_prefix}/deposition_metadata/{DEPOSITION_ID1}/Images/snapshot.png",
        "key_photo_thumbnail_url": f"{http_prefix}/deposition_metadata/{DEPOSITION_ID1}/Images/thumbnail.png",
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
        "title": "Deposition 2",
        "description": "A really awesome deposition",
        "deposition_date": date(2023, 4, 2),
        "release_date": date(2024, 6, 1),
        "last_modified_date": date(2023, 9, 2),
        "related_database_entries": "EMPIAR-1000, EMDB-1001",
        "deposition_publications": "doi:10.1000/1234",
        "s3_prefix": f"s3://test-public-bucket/depositions_metadata/{DEPOSITION_ID2}/",
        "https_prefix": f"{http_prefix}/depositions_metadata/{DEPOSITION_ID2}/",
        "deposition_types": "annotation,tomogram",
        "key_photo_url": None,
        "key_photo_thumbnail_url": None,
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
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    expected_deposition2: dict[str, Any],
    expected_dep2_authors: list[dict[str, Any]],
) -> None:
    verify_dataset_import(["--import-depositions", "--deposition-id", DEPOSITION_ID2])
    actual = models.Deposition.get(id=DEPOSITION_ID2)
    verify_model(actual, expected_deposition2)
    assert len(actual.authors) == 3
    actual_authors = list(actual.authors.order_by(models.DepositionAuthor.author_list_order))
    for i, author in enumerate(actual_authors):
        verify_model(author, expected_dep2_authors[i])


# Tests update of deposition existing in database, and addition of new authors, updating entries already existing in
# db, and removing stale authors
def test_import_deposition_update(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    expected_deposition1: dict[str, Any],
    expected_dep1_authors: list[dict[str, Any]],
) -> None:
    populate_deposition()
    populate_deposition_authors()
    verify_dataset_import(["--import-depositions", "--deposition-id", DEPOSITION_ID1])
    actual = models.Deposition.get(id=DEPOSITION_ID1)
    verify_model(actual, expected_deposition1)
    assert len(actual.authors) == 2
    actual_authors = list(actual.authors.order_by(models.DepositionAuthor.author_list_order))
    for i, author in enumerate(actual_authors):
        verify_model(author, expected_dep1_authors[i])


# Tests importing related entity doesn't update the deposition when no import specified
def test_import_deposition_no_update(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
) -> None:
    populate_deposition()
    populate_deposition_authors()
    verify_dataset_import([])
    actual = models.Deposition.get(id=DEPOSITION_ID1)
    verify_model(actual, stale_deposition_metadata())
    assert len(actual.authors) == 1
    actual_authors = list(actual.authors.order_by(models.DepositionAuthor.author_list_order))
    verify_model(actual_authors[0], stale_deposition_author())
