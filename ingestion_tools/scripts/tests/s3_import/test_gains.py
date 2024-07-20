import subprocess
from os.path import basename
from unittest.mock import Mock

import pytest
from importers.dataset import DatasetImporter
from importers.gain import GainImporter
from importers.run import RunImporter
from mypy_boto3_s3 import S3Client
from standardize_dirs import IMPORTERS
from tests.s3_import.util import list_dir

from common.config import DepositionImportConfig
from common.fs import FileSystemApi


def create_file_locally(*args, **kwargs):
    local_output = args[0][2]
    with open(local_output, "w") as f:
        f.write("test")


@pytest.fixture
def config(s3_fs: FileSystemApi, test_output_bucket: str) -> DepositionImportConfig:
    output_path = f"{test_output_bucket}/output"
    input_bucket = "test-public-bucket"
    import_config = "tests/fixtures/dataset1.yaml"
    return DepositionImportConfig(s3_fs, import_config, output_path, input_bucket, IMPORTERS)


def test_non_dm4_gains_import(
    config: DepositionImportConfig,
    test_output_bucket: str,
    s3_client: S3Client,
) -> None:
    datasets = list(DatasetImporter.finder(config))
    runs = list(RunImporter.finder(config, dataset=datasets[0]))
    gains = list(GainImporter.finder(config, dataset=datasets[0], run=runs[0]))
    for gain in gains:
        gain.import_item()

    dataset_name = datasets[0].name
    run_name = runs[0].name
    prefix = f"output/{dataset_name}/{run_name}/Frames"
    gain_files = [basename(item) for item in list_dir(s3_client, test_output_bucket, prefix)]
    assert f"{run_name}_gain.gain" in gain_files


def test_dm4_gains_import(
    config: DepositionImportConfig,
    test_output_bucket: str,
    s3_client: S3Client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    subprocess_mock = Mock(spec="subprocess.check_output", side_effect=create_file_locally)
    monkeypatch.setattr(subprocess, "check_output", subprocess_mock)

    datasets = list(DatasetImporter.finder(config))
    runs = list(RunImporter.finder(config, dataset=datasets[0]))
    gains = list(GainImporter.finder(config, dataset=datasets[0], run=runs[1]))
    for gain in gains:
        gain.import_item()

    dataset_name = datasets[0].name
    run_name = runs[1].name
    prefix = f"output/{dataset_name}/{run_name}/Frames"
    gain_files = [basename(item) for item in list_dir(s3_client, test_output_bucket, prefix)]
    assert f"{run_name}_gain.mrc" in gain_files
