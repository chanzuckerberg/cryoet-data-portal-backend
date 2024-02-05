import json

from common.config import DataImportConfig
from importers.dataset import DatasetImporter
from importers.dataset_key_photo import DatasetKeyPhotoImporter
from common.fs import FileSystemApi
from mypy_boto3_s3 import S3Client


def test_import_dataset_metadata(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    config_file = "tests/fixtures/dataset1.yaml"
    output_path = f"{test_output_bucket}/output"
    input_bucket = "input_bucket"
    config = DataImportConfig(s3_fs, config_file, output_path, input_bucket)
    dataset = DatasetImporter(config, None)
    dataset.import_metadata(output_path)

    output = s3_fs.open(f"{output_path}/10001/dataset_metadata.json", "r").read()
    metadata = json.loads(output)
    assert metadata["dataset_title"] == "Dataset 1"


def test_key_photo_import_http(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config_file = "tests/fixtures/dataset1.yaml"
    output_prefix = "output"
    output_path = f"{test_output_bucket}/{output_prefix}"
    input_bucket = "test-public-bucket"
    config = DataImportConfig(s3_fs, config_file, output_path, input_bucket)

    dataset = DatasetImporter(config, None)
    dataset_key_photos_importer = DatasetKeyPhotoImporter.find_dataset_key_photos(config, dataset)
    dataset_key_photos_importer.import_key_photo()
    dataset.import_metadata(output_path)

    output = s3_fs.open(f"{output_path}/10001/dataset_metadata.json", "r").read()
    metadata = json.loads(output)
    assert metadata["dataset_title"] == "Dataset 1"

    files = s3_client.list_objects(Bucket=test_output_bucket, Prefix=f"{output_prefix}/10001/Images")
    s3_files: list[str] = []
    for item in files["Contents"]:
        s3_files.append(item["Key"])
    num_key_photos = 0
    for key, path in metadata["key_photos"].items():
        num_key_photos += 1
        assert key in ["snapshot", "thumbnail"]
        assert path.startswith("10001/Images/")
        assert f"{output_prefix}/{path}" in s3_files
    assert num_key_photos == 2
