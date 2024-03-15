import datetime
from typing import Generator, Any, Callable

import pytest
from click.testing import CliRunner
import common.db_models as models
from mypy_boto3_s3 import S3Client
from peewee import SqliteDatabase
from db_import import load


DATASET_ID = 30001


def populate_dataset_author_table() -> None:
    models.DatasetAuthor(id=1, dataset_id=10000, name="Julia Child", author_list_order=1).save(force_insert=True)
    models.DatasetAuthor(id=2, dataset_id=DATASET_ID, name="Stale Author", author_list_order=1).save(force_insert=True)
    models.DatasetAuthor(id=3, dataset_id=DATASET_ID, name="Virginia Woolf", author_list_order=3).save(force_insert=True)


def populate_dataset_funding_table() -> None:
    models.DatasetFunding(id=1, dataset_id=10000, funding_agency_name="Grant Provider 1").save(force_insert=True)
    models.DatasetFunding(
        id=2, dataset_id=DATASET_ID, funding_agency_name="Grant Provider 1", grant_id="foo"
    ).save(force_insert=True)
    # TODO: Add functionality to remove stale data
    # models.DatasetFunding(id=3, dataset_id=DATASET_ID, funding_agency_name="Grant Provider 2").save(force_insert=True)
    models.DatasetFunding(id=3, dataset_id=10000, funding_agency_name="Grant Provider 2").save(force_insert=True)


@pytest.fixture
def verify_dataset_import(
        mock_db: Generator[SqliteDatabase, Any, None],
        s3_client: S3Client,
        default_inputs: list[str],
        verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
        dataset_30001_expected: dict[str, Any]
) -> Callable[[list[str], int, int], models.Dataset]:
    def _verify(additional_inputs: list[str], authors_count: int, funding_source_count: int) -> models.Dataset:
        input_args = default_inputs + ["--s3_prefix", str(DATASET_ID)] + additional_inputs
        CliRunner().invoke(load, input_args)
        actual = models.Dataset.get(id=DATASET_ID)
        verify_model(actual, dataset_30001_expected)
        assert len(actual.authors) == authors_count
        assert len(actual.funding_sources) == funding_source_count
        return actual
    return _verify


# Tests addition of new dataset to database
def test_import_dataset_new(
    verify_dataset_import: Callable[[list[str], int, int], models.Dataset],
) -> None:
    verify_dataset_import([], 0, 0)


# Tests update of dataset existing in database
def test_import_dataset_update(
    verify_dataset_import: Callable[[list[str], int, int], models.Dataset],
) -> None:
    today = datetime.date.today()
    models.Dataset(
        id=DATASET_ID, title="foo", description="bar", deposition_date=today, release_date=today, last_modified_date=today, sample_type="test", s3_prefix="s3://invalid_bucket/", https_prefix="https://invalid-site.com/1234"
    ).save(force_insert=True)
    verify_dataset_import([], 0, 0)


# Tests addition of new authors, updating entries already existing in db, and removing stale authors
def test_import_dataset_and_dataset_authors(
    verify_dataset_import: Callable[[list[str], int, int], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    dataset_30001_authors_expected: list[dict[str, Any]],
) -> None:
    populate_dataset_author_table()
    actual = verify_dataset_import(["--import-dataset-authors"], len(dataset_30001_authors_expected), 0)
    actual_authors = [author for author in actual.authors.order_by(models.DatasetAuthor.author_list_order)]
    for i, author in enumerate(actual_authors):
        verify_model(author, dataset_30001_authors_expected[i])


# Tests addition of new funding sources, and updating entries already existing in db
def test_import_dataset_and_dataset_funding(
    verify_dataset_import: Callable[[list[str], int, int], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    dataset_30001_funding_expected: list[dict[str, Any]],
) -> None:
    populate_dataset_funding_table()
    actual = verify_dataset_import(["--import-dataset-funding"], 0, len(dataset_30001_funding_expected))
    actual_funding_sources = [author for author in actual.funding_sources]
    for i, funding_sources in enumerate(actual_funding_sources):
        verify_model(funding_sources, dataset_30001_funding_expected[i])
