import json

from importers.dataset import DatasetImporter
from importers.dataset_key_photo import DatasetKeyPhotoImporter
from mypy_boto3_s3 import S3Client
from standardize_dirs import IMPORTERS
from tests.s3_import.util import list_dir

from common.config import DepositionImportConfig
from common.fs import FileSystemApi


def test_import_dataset_metadata(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    config_file = "tests/fixtures/dataset1.yaml"
    output_path = f"{test_output_bucket}/output"
    input_bucket = "input_bucket"
    config = DepositionImportConfig(s3_fs, config_file, output_path, input_bucket, IMPORTERS)
    dataset = list(DatasetImporter.finder(config))[0]
    dataset.import_metadata()

    with s3_fs.open(f"{output_path}/10001/dataset_metadata.json", "r") as fh:
        output = fh.read()
    metadata = json.loads(output)
    assert metadata["dataset_title"] == "Dataset 1"


def test_key_photo_import_http(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config_file = "tests/fixtures/dataset1.yaml"
    output_prefix = "output"
    output_path = f"{test_output_bucket}/{output_prefix}"
    input_bucket = "test-public-bucket"
    config = DepositionImportConfig(s3_fs, config_file, output_path, input_bucket, IMPORTERS)

    dataset = list(DatasetImporter.finder(config))[0]
    keyphotos = DatasetKeyPhotoImporter.finder(config, dataset=dataset)
    for item in keyphotos:
        item.import_item()
    dataset.import_metadata()

    with s3_fs.open(f"{output_path}/10001/dataset_metadata.json", "r") as fh:
        output = fh.read()
    metadata = json.loads(output)
    assert metadata["dataset_title"] == "Dataset 1"

    s3_files = list_dir(s3_client, test_output_bucket, f"{output_prefix}/10001/Images", assert_non_zero_size=True)

    # Make sure the files are in our metadata and match our s3 file paths
    for key, path in metadata["key_photos"].items():
        assert key in ["snapshot", "thumbnail"]
        assert path.startswith("10001/Images/")
        assert f"{output_prefix}/{path}" in s3_files
    assert len(metadata["key_photos"]) == 2
