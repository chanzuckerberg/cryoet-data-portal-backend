import json

from importers.dataset import DatasetImporter
from importers.dataset_key_photo import DatasetKeyPhotoImporter
from importers.deposition import DepositionImporter
from importers.utils import IMPORTERS
from mypy_boto3_s3 import S3Client

from common.config import DepositionImportConfig
from common.fs import FileSystemApi
from tests.s3_import.util import list_dir


def test_import_dataset_metadata(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    config_file = "tests/fixtures/dataset1.yaml"
    output_path = f"{test_output_bucket}/output"
    input_bucket = "test-public-bucket"
    config = DepositionImportConfig(s3_fs, config_file, output_path, input_bucket, IMPORTERS)
    deposition = list(DepositionImporter.finder(config))[0]
    dataset = list(DatasetImporter.finder(config, deposition=deposition))[0]
    dataset.import_metadata()

    with s3_fs.open(f"{output_path}/10001/dataset_metadata.json", "r") as fh:
        output = fh.read()
    metadata = json.loads(output)
    assert metadata["dataset_title"] == "Dataset 1"
    assert metadata["deposition_id"] == "10301"


def test_no_import_dataset_metadata_and_key_photo(
    s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client,
) -> None:
    config_file = "tests/fixtures/dataset1.yaml"
    output_path = f"{test_output_bucket}/output"
    input_bucket = "test-public-bucket"
    config = DepositionImportConfig(s3_fs, config_file, output_path, input_bucket, IMPORTERS)
    deposition = list(DepositionImporter.finder(config))[0]
    dataset = list(DatasetImporter.finder(config, deposition=deposition))[0]
    dataset.allow_imports = False
    keyphotos = DatasetKeyPhotoImporter.finder(config, dataset=dataset)
    for item in keyphotos:
        item.allow_imports = False
        item.import_item()
    dataset.import_metadata()

    actual = list_dir(s3_client, test_output_bucket, "output/10001/")
    assert actual == []
