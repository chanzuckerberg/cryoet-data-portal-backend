import subprocess
from os.path import basename
from unittest.mock import Mock

import pytest
from importers.gain import GainImporter
from importers.utils import IMPORTERS
from mypy_boto3_s3 import S3Client

from common.config import DepositionImportConfig
from common.fs import FileSystemApi
from tests.s3_import.util import create_config, get_dataset_and_run, list_dir


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
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    s3_client: S3Client,
) -> None:
    config = create_config(s3_fs, test_output_bucket)
    dataset, run = get_dataset_and_run(config)
    gains = list(GainImporter.finder(config, dataset=dataset, run=run))
    for gain in gains:
        gain.import_item()
    run_name = run.name
    prefix = f"output/{dataset.name}/{run_name}/Gains"
    gain_files = [basename(item) for item in list_dir(s3_client, test_output_bucket, prefix)]
    assert f"CountRef_{run_name}.gain" in gain_files


def test_dm4_gains_import(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    s3_client: S3Client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    subprocess_mock = Mock(spec="subprocess.check_output", side_effect=create_file_locally)
    monkeypatch.setattr(subprocess, "check_output", subprocess_mock)

    config = create_config(s3_fs, test_output_bucket)
    dataset, run = get_dataset_and_run(config, run_index=1)
    gains = list(GainImporter.finder(config, dataset=dataset, run=run))
    for gain in gains:
        gain.import_item()
    run_name = run.name
    prefix = f"output/{dataset.name}/{run_name}/Gains"
    gain_files = [basename(item) for item in list_dir(s3_client, test_output_bucket, prefix)]
    assert f"CountRef_{run_name}.mrc" in gain_files
