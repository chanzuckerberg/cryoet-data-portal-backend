import os.path
from typing import List

from botocore.response import StreamingBody
from importers.base_importer import BaseImporter
from importers.dataset import DatasetImporter
from importers.deposition import DepositionImporter
from importers.run import RunImporter
from importers.utils import IMPORTERS
from mypy_boto3_s3 import S3Client

from common.config import DepositionImportConfig
from common.fs import FileSystemApi


def list_dir(s3_client: S3Client, bucket: str, prefix: str, assert_non_zero_size: bool = False) -> List[str]:
    files = s3_client.list_objects(Bucket=bucket, Prefix=prefix)
    if assert_non_zero_size:
        for item in files["Contents"]:
            assert item["Size"] > 0
    return [item["Key"] for item in files["Contents"]] if "Contents" in files else []


def create_config(s3_fs: FileSystemApi, test_output_bucket: str, config_path: str = None, https_prefix: str = None) -> DepositionImportConfig:
    output_path = f"{test_output_bucket}/output"
    input_bucket = "test-public-bucket"
    if config_path is None:
        config_path = "dataset1.yaml"
    import_config = f"tests/fixtures/{config_path}"
    return DepositionImportConfig(s3_fs, import_config, output_path, input_bucket, IMPORTERS, https_prefix=https_prefix)


def get_run_and_parents(
    config: DepositionImportConfig,
    deposition_index: int = 0,
    dataset_index: int = 0,
    run_index: int = 0,
) -> dict[str, BaseImporter]:
    deposition = list(DepositionImporter.finder(config))[deposition_index]
    parents = {"deposition": deposition}
    parents["dataset"] = list(DatasetImporter.finder(config, **parents))[dataset_index]
    parents["run"] = list(RunImporter.finder(config, **parents))[run_index]
    return parents


def get_data_from_s3(s3_client: S3Client, bucket_name: str, path: str) -> StreamingBody:
    return s3_client.get_object(Bucket=bucket_name, Key=path)["Body"]


def get_raw_data_from_s3(s3_client: S3Client, bucket_name: str, path: str) -> StreamingBody:
    return s3_client.get_object(Bucket=bucket_name, Key=path)


def get_children(s3_client: S3Client, bucket: str, prefix: str, recurse: bool = False) -> set[str]:
    all_descendants = {os.path.relpath(item, prefix) for item in list_dir(s3_client, bucket, prefix)}
    if recurse:
        return all_descendants

    def get_root_folder(path):
        while os.path.dirname(path) != path and "/" in path:
            path = os.path.dirname(path)
        return path

    return {get_root_folder(item) if "/" in item else item for item in all_descendants}


def validate_output_data_is_same_as_source(
        s3_client: S3Client,
        output_bucket: str,
        prefix: str,
        importer: BaseImporter,
):
    source_filepaths = [importer.path] if importer.path else importer.file_paths
    actual_files = [os.path.basename(item) for item in list_dir(s3_client, output_bucket, prefix)]
    for source_filepath in source_filepaths:
        source_filename = os.path.basename(source_filepath)
        assert source_filename in actual_files

        actual = get_data_from_s3(s3_client, output_bucket, os.path.join(prefix, source_filename)).readlines()
        source_bucket_key = "/".join(source_filepath.split("/")[1:])
        expected = get_data_from_s3(s3_client, "test-public-bucket", source_bucket_key).readlines()
        assert actual == expected
