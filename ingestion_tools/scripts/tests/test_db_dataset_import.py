from datetime import date
from typing import Generator, Any

from importers.db.base_importer import DBImportConfig
import common.db_models as models
from importers.db.dataset import DatasetDBImporter
from mypy_boto3_s3 import S3Client
from peewee import SqliteDatabase


def test_import_dataset_that_exists(mock_db: Generator[SqliteDatabase, Any, None], s3_client: S3Client) -> None:
    config = DBImportConfig(s3_client=s3_client, bucket_name="test-public-bucket", https_prefix="https://foo.com")
    dataset_id = 30001
    datasets = DatasetDBImporter.get_items(config, str(dataset_id))
    for dataset in datasets:
        dataset.import_to_db()
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
    assert actual.https_prefix == f"https://foo.com/{dataset_id}/"
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
    assert actual.key_photo_url == f"https://foo.com/{dataset_id}/KeyPhoto/snapshot.png"
    assert actual.key_photo_thumbnail_url == f"https://foo.com/{dataset_id}/KeyPhoto/thumbnail.png"
