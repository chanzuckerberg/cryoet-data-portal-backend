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


def create_config(s3_fs: FileSystemApi, test_output_bucket: str, config_path: str = None) -> DepositionImportConfig:
    output_path = f"{test_output_bucket}/output"
    input_bucket = "test-public-bucket"
    if config_path is None:
        config_path = "dataset1.yaml"
    import_config = f"tests/fixtures/{config_path}"
    return DepositionImportConfig(s3_fs, import_config, output_path, input_bucket, IMPORTERS)


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


def get_children(s3_client: S3Client, bucket: str, prefix: str, recurse: bool = False) -> set[str]:
    all_descendants = {os.path.relpath(item, prefix) for item in list_dir(s3_client, bucket, prefix)}
    if recurse:
        return all_descendants

    def get_root_folder(path):
        while os.path.dirname(path) != path and "/" in path:
            path = os.path.dirname(path)
        return path

    return {get_root_folder(item) if "/" in item else item for item in all_descendants}
