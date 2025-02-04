import os.path

from importers.base_importer import BaseImporter
from importers.rawtilt import RawTiltImporter
from importers.tiltseries import TiltSeriesImporter
from mypy_boto3_s3 import S3Client

from common.config import DepositionImportConfig
from common.fs import FileSystemApi
from tests.s3_import.util import create_config, get_run_and_parents, list_dir, validate_output_data_is_same_as_source


def get_parents(config: DepositionImportConfig) -> dict[str, BaseImporter]:
    parents = get_run_and_parents(config)
    parents["tiltseries"] = next(TiltSeriesImporter.finder(config, **parents))
    return parents


def test_raw_tilt_import(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_parents(config)
    rawtilts_importer = list(RawTiltImporter.finder(config, **parents))[0]

    rawtilts_importer.import_item()

    run_name = parents["run"].name
    prefix = f"output/{parents['dataset'].name}/{run_name}/TiltSeries/100"
    validate_output_data_is_same_as_source(s3_client, test_output_bucket, prefix, rawtilts_importer)


def test_raw_tilt_no_import(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_run_and_parents(config)
    rawtilts_importer = list(RawTiltImporter.finder(config, **parents))[0]

    rawtilts_importer.allow_imports = False
    rawtilts_importer.import_item()

    prefix = f"output/{parents['dataset'].name}/{parents['run'].name}/TiltSeries"
    actual_files = [os.path.basename(item) for item in list_dir(s3_client, test_output_bucket, prefix)]
    assert actual_files == []
