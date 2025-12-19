import os.path
from os.path import basename

from importers.collection_metadata import CollectionMetadataImporter
from mypy_boto3_s3 import S3Client

from common.fs import FileSystemApi
from tests.s3_import.util import create_config, get_data_from_s3, get_run_and_parents, list_dir


def test_collection_metadata_import(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_run_and_parents(config)
    collection_metadata = list(CollectionMetadataImporter.finder(config, **parents))
    for item in collection_metadata:
        item.import_item()

    run_name = parents["run"].name
    prefix = f"output/{parents['dataset'].name}/{run_name}/Frames"
    actual_files = [basename(item) for item in list_dir(s3_client, test_output_bucket, prefix)]
    assert f"{run_name}.mdoc" in actual_files

    actual = get_data_from_s3(s3_client, test_output_bucket, os.path.join(prefix, f"{run_name}.mdoc")).readlines()
    source_file_path = "/".join(collection_metadata[0].path.split("/")[1:])
    expected = get_data_from_s3(s3_client, "test-public-bucket", source_file_path).readlines()
    assert actual == expected


def test_collection_metadata_no_import(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_run_and_parents(config)
    collection_metadata = list(CollectionMetadataImporter.finder(config, **parents))
    for item in collection_metadata:
        item.allow_imports = False
        item.import_item()
    prefix = f"output/{parents['dataset'].name}/{parents['run'].name}/Frames"
    actual_files = [basename(item) for item in list_dir(s3_client, test_output_bucket, prefix)]
    assert actual_files == []
