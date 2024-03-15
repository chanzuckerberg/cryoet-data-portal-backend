from datetime import date
from typing import Generator, Any

from click.testing import CliRunner
import common.db_models as models
from mypy_boto3_s3 import S3Client
from peewee import SqliteDatabase
from db_import import load


def test_import_dataset_that_exists(
        mock_db: Generator[SqliteDatabase, Any, None],
        s3_client: S3Client,
        default_inputs: list[str],
        http_prefix: str
) -> None:
    dataset_id = 30001
    runner = CliRunner()
    default_inputs += ["--s3_prefix", str(dataset_id)]
    runner.invoke(load, default_inputs)
    actual = models.Dataset.get(id=dataset_id)

    assert actual.id == dataset_id
    assert actual.title == "Lorem ipsum dolor"
    assert (
        actual.description
        == "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et "
        "dolore magna aliqua."
    )
    assert actual.deposition_date == date(2023, 4, 1)
    assert actual.release_date == date(2023, 6, 2)
    assert actual.last_modified_date == date(2023, 8, 5)
    assert actual.s3_prefix == f"s3://test-public-bucket/{dataset_id}/"
    assert actual.https_prefix == f"{http_prefix}/{dataset_id}/"
    assert actual.organism_name == "Foo Bar"
    assert actual.organism_taxid == "1111"
    assert actual.tissue_name == "test-tissue1"
    assert actual.tissue_id == "1234"
    assert actual.cell_name == "foo"
    assert actual.cell_type_id == "4321"
    assert actual.cell_strain_id == "999999"
    assert actual.cell_strain_name == "test value"
    assert actual.cell_component_name == "tail"
    assert actual.cell_component_id == "GO:123435"
    assert actual.sample_preparation == "method1: value1, method2: value3"
    assert actual.grid_preparation == "method3: value8, method6: value4"
    assert actual.related_database_entries == "TEST-1243435"
    assert actual.dataset_publications == "test-publication-data"
    assert actual.dataset_citations == "10.1101/2024.01.12.111111"
    assert actual.key_photo_url == f"{http_prefix}/{dataset_id}/KeyPhoto/snapshot.png"
    assert actual.key_photo_thumbnail_url == f"{http_prefix}/{dataset_id}/KeyPhoto/thumbnail.png"
