from typing import Generator, Any, Callable

from click.testing import CliRunner
import common.db_models as models
from mypy_boto3_s3 import S3Client
from peewee import SqliteDatabase
from db_import import load


def populate_dataset_author_table(dataset_id: int) -> None:
    models.DatasetAuthor(id=1, dataset_id=10000, name="Julia Child", author_list_order=1).save(force_insert=True)
    models.DatasetAuthor(id=2, dataset_id=dataset_id, name="Stale Author", author_list_order=1).save(force_insert=True)
    models.DatasetAuthor(id=3, dataset_id=dataset_id, name="Virginia Woolf", author_list_order=3).save(force_insert=True)


def test_import_dataset_insert(
    mock_db: Generator[SqliteDatabase, Any, None],
    s3_client: S3Client,
    default_inputs: list[str],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    dataset_30001_expected: dict[str, Any],
) -> None:
    dataset_id = 30001
    default_inputs += ["--s3_prefix", str(dataset_id)]
    CliRunner().invoke(load, default_inputs)
    actual = models.Dataset.get(id=dataset_id)
    verify_model(actual, dataset_30001_expected)
    assert len(actual.authors) == 0


def test_import_dataset_and_dataset_authors(
    mock_db: Generator[SqliteDatabase, Any, None],
    s3_client: S3Client,
    default_inputs: list[str],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    dataset_30001_expected: dict[str, Any],
    dataset_30001_authors_expected: list[dict[str, Any]],
) -> None:
    dataset_id = 30001
    populate_dataset_author_table(dataset_id)
    default_inputs += ["--s3_prefix", str(dataset_id), "--import-dataset-authors"]
    CliRunner().invoke(load, default_inputs)
    actual = models.Dataset.get(id=dataset_id)
    verify_model(actual, dataset_30001_expected)
    actual_authors = [author for author in actual.authors.order_by(models.DatasetAuthor.author_list_order)]
    assert len(actual_authors) == len(dataset_30001_authors_expected)
    for i, author in enumerate(actual_authors):
        verify_model(author, dataset_30001_authors_expected[i])
