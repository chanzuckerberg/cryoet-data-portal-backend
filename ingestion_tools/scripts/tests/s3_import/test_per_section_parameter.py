import json

from importers.base_importer import BaseImporter
from importers.collection_metadata import CollectionMetadataImporter
from importers.ctf import CtfImporter
from importers.db.base_importer import S3Client
from importers.rawtilt import RawTiltImporter
from importers.tiltseries import PerSectionParameterGenerator, TiltSeriesImporter

from common.config import DepositionImportConfig
from common.fs import FileSystemApi
from tests.s3_import.util import create_config, get_run_and_parents


def get_parents(config: DepositionImportConfig) -> dict[str, BaseImporter]:
    parents = get_run_and_parents(config)
    parents["tiltseries"] = next(TiltSeriesImporter.finder(config, **parents))
    return parents


def setup_psp_generator(s3_fs: FileSystemApi, test_output_bucket: str, config_path: str=None) -> PerSectionParameterGenerator:
    config = create_config(s3_fs, test_output_bucket, config_path)
    parents = get_parents(config)
    for mdoc_importer in CollectionMetadataImporter.finder(config, **parents):
        mdoc_importer.import_item()

    for raw_tlt_importer in RawTiltImporter.finder(config, **parents):
        raw_tlt_importer.import_item()

    for ctf_importer in CtfImporter.finder(config, **parents):
        ctf_importer.import_item()
    return PerSectionParameterGenerator(config, parents)


def test_per_section_parameter_success(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    psp_generator = setup_psp_generator(s3_fs, test_output_bucket)
    actual = psp_generator.get_data()
    print(json.dumps({"psp":actual}, indent=2))
    assert len(actual) == 5
