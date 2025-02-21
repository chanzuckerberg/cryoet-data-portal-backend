import os.path
from unittest.mock import Mock

import importers.ctf as ctf
import pytest
from importers.base_importer import BaseImporter
from importers.tiltseries import TiltSeriesImporter
from mypy_boto3_s3 import S3Client

import common.ctf_converter
from common.config import DepositionImportConfig
from common.fs import FileSystemApi
from tests.s3_import.util import create_config, get_run_and_parents, list_dir, validate_output_data_is_same_as_source


def get_parents(config: DepositionImportConfig) -> dict[str, BaseImporter]:
    parents = get_run_and_parents(config)
    parents["tiltseries"] = next(TiltSeriesImporter.finder(config, **parents))
    return parents

def test_ctf_import(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_parents(config)
    ctf_importer = list(ctf.CtfImporter.finder(config, **parents))[0]

    ctf_importer.import_item()

    run_name = parents["run"].name
    prefix = f"output/{parents['dataset'].name}/{run_name}/TiltSeries/100"
    validate_output_data_is_same_as_source(s3_client, test_output_bucket, prefix, ctf_importer)

def test_ctf_get_output_data(
        s3_fs: FileSystemApi,
        test_output_bucket: str,
        s3_client: S3Client,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_parents(config)
    ctf_importer = list(ctf.CtfImporter.finder(config, **parents))[0]

    mock_ctf_info = Mock(spec=common.ctf_converter.CTFInfo)
    mock_ctf_factory = Mock(spec=common.ctf_converter.BaseCTFConverter)
    mock_ctf_factory.get_ctf_info.return_value = mock_ctf_info
    mock_ctf_converter_factory = Mock(spec=common.ctf_converter.ctf_converter_factory, return_value=mock_ctf_factory)
    monkeypatch.setattr(ctf, "ctf_converter_factory", mock_ctf_converter_factory)
    assert ctf_importer.get_output_data() == mock_ctf_info
    path = (f"{test_output_bucket}/output/{parents['dataset'].name}/{parents['run'].name}/TiltSeries/100"
            f"/{os.path.basename(ctf_importer.path)}")
    mock_ctf_converter_factory.assert_called_once_with(ctf_importer.metadata, config, path)

def test_ctf_no_import(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_run_and_parents(config)
    ctf_importer = list(ctf.CtfImporter.finder(config, **parents))[0]

    ctf_importer.allow_imports = False
    ctf_importer.import_item()

    prefix = f"output/{parents['dataset'].name}/{parents['run'].name}/TiltSeries"
    actual_files = [os.path.basename(item) for item in list_dir(s3_client, test_output_bucket, prefix)]
    assert actual_files == []
