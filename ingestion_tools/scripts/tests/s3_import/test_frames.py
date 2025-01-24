import os.path
from os.path import basename

from importers.frame import FrameImporter
from mypy_boto3_s3 import S3Client

from common.fs import FileSystemApi
from tests.s3_import.util import create_config, get_data_from_s3, get_run_and_parents, list_dir


def test_frames_import(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_run_and_parents(config)
    frames = list(FrameImporter.finder(config, **parents))
    for item in frames:
        item.import_item()

    run_name = parents["run"].name
    prefix = f"output/{parents['dataset'].name}/{run_name}/Frames"
    actual_files = [basename(item) for item in list_dir(s3_client, test_output_bucket, prefix)]
    source_filename = os.path.basename(frames[0].path)
    assert source_filename in actual_files

    actual = get_data_from_s3(s3_client, test_output_bucket, os.path.join(prefix, source_filename))["Body"].readlines()
    source_file_path = "/".join(frames[0].path.split("/")[1:])
    expected = get_data_from_s3(s3_client, "test-public-bucket", source_file_path)["Body"].readlines()
    assert actual == expected


def test_frames_no_import(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_run_and_parents(config)
    frames = list(FrameImporter.finder(config, **parents))
    for item in frames:
        item.allow_imports = False
        item.import_item()

    prefix = f"output/{parents['dataset'].name}/{parents['run'].name}/Frames"
    actual_files = [basename(item) for item in list_dir(s3_client, test_output_bucket, prefix)]
    assert actual_files == []
