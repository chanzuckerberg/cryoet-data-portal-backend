import os.path
from os.path import basename

from importers.collection_metadata import CollectionMetadataImporter
from mypy_boto3_s3 import S3Client

from common.fs import FileSystemApi
from tests.s3_import.util import create_config, get_data_from_s3, get_dataset_and_run, list_dir


def test_collection_metadata_import(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config = create_config(s3_fs, test_output_bucket)
    dataset, run = get_dataset_and_run(config)
    collection_metadata = list(CollectionMetadataImporter.finder(config, dataset=dataset, run=run))
    for item in collection_metadata:
        item.import_item()

    run_name = run.name
    prefix = f"output/{dataset.name}/{run_name}/Frames"
    actual_files = [basename(item) for item in list_dir(s3_client, test_output_bucket, prefix)]
    source_filename = os.path.basename(collection_metadata[0].path)
    assert source_filename in actual_files

    actual = get_data_from_s3(s3_client, test_output_bucket, os.path.join(prefix, source_filename)).readlines()
    source_file_path = "/".join(collection_metadata[0].path.split("/")[1:])
    expected = get_data_from_s3(s3_client, "test-public-bucket", source_file_path).readlines()
    assert actual == expected
