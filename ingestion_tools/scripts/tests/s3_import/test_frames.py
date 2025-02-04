import os.path

from importers.frame import FrameImporter
from mypy_boto3_s3 import S3Client

from common.fs import FileSystemApi
from tests.s3_import.util import create_config, get_run_and_parents, list_dir, validate_output_data_is_same_as_source


def test_frames_import(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_run_and_parents(config)
    frames_importer = list(FrameImporter.finder(config, **parents))[0]

    frames_importer.import_item()

    run_name = parents["run"].name
    prefix = f"output/{parents['dataset'].name}/{run_name}/Frames"
    validate_output_data_is_same_as_source(s3_client, test_output_bucket, prefix, frames_importer)


def test_frames_no_import(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_run_and_parents(config)
    frames = list(FrameImporter.finder(config, **parents))
    for item in frames:
        item.allow_imports = False
        item.import_item()

    prefix = f"output/{parents['dataset'].name}/{parents['run'].name}/Frames"
    actual_files = [os.path.basename(item) for item in list_dir(s3_client, test_output_bucket, prefix)]
    assert actual_files == []
