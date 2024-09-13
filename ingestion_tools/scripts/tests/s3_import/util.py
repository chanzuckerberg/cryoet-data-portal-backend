from typing import List

from importers.dataset import DatasetImporter
from importers.run import RunImporter
from mypy_boto3_s3 import S3Client
from standardize_dirs import IMPORTERS

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


def get_dataset_and_run(
    config: DepositionImportConfig, dataset_index: int = 0, run_index: int = 0,
) -> tuple[DatasetImporter, RunImporter]:
    dataset = list(DatasetImporter.finder(config))[dataset_index]
    run = list(RunImporter.finder(config, dataset=dataset))[run_index]
    return dataset, run
