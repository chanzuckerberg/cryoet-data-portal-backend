import pytest
from importers.base_importer import BaseImporter
from importers.collection_metadata import CollectionMetadataImporter
from importers.ctf import CtfImporter
from importers.db.base_importer import S3Client
from importers.rawtilt import RawTiltImporter
from importers.tiltseries import PerSectionParameterGenerator, TiltSeriesImporter

from common.config import DepositionImportConfig
from common.fs import FileSystemApi
from tests.s3_import.util import create_config, get_run_and_parents


@pytest.fixture
def expected_output() -> list[tuple[int, float, float, float, float, float, float]]:
    return [
        (3, -4.38, None, None, None, None, None),
        (2, -1.98, -46.02, 3.0, 45.0, -46.02, 3574.0),
        (0, -0.00499939, -52.02, 1.0, 60.0, -52.02, 3345.0),
        (1, 2.013, -49.02, 2.0, 19.0, -49.02, 3309.0),
    ]


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


def test_psp_success(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client, expected_output: list[tuple[int, float, float, float, float, float, float]]) -> None:
    psp_generator = setup_psp_generator(s3_fs, test_output_bucket)
    actual = psp_generator.get_data()
    assert len(actual) == len(expected_output)
    for i, expected_entry in enumerate(expected_output):
        assert actual[i]["z_index"] == i
        assert actual[i]["frame_acquisition_order"] == expected_entry[0]
        assert actual[i]["raw_angle"] == expected_entry[1]
        assert actual[i]["astigmatic_angle"] == expected_entry[2]
        assert actual[i]["major_defocus"] == expected_entry[3]
        assert actual[i]["max_resolution"] == expected_entry[4]
        assert actual[i]["minor_defocus"] == expected_entry[5]
        assert actual[i]["phase_shift"] == expected_entry[6]


def test_psp_no_mdoc(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    psp_generator = setup_psp_generator(s3_fs, test_output_bucket)
    psp_generator.config.object_configs.pop("collection_metadata")

    with pytest.raises(FileNotFoundError):
        psp_generator.get_data()


def test_psp_no_rawtlt(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    psp_generator = setup_psp_generator(s3_fs, test_output_bucket)
    psp_generator.config.object_configs.pop("rawtilt")

    with pytest.raises(FileNotFoundError):
        psp_generator.get_data()


def test_psp_mdoc_rawtlt_mismatch(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    psp_generator = setup_psp_generator(s3_fs, test_output_bucket, "tiltseries/invalid_mdoc_rawtlt.yaml")

    with pytest.raises(KeyError):
        psp_generator.get_data()


def test_psp_no_ctf(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client, expected_output: list[tuple[int, float, float, float, float, float, float]]) -> None:
    psp_generator = setup_psp_generator(s3_fs, test_output_bucket)
    psp_generator.config.object_configs.pop("ctf")

    actual = psp_generator.get_data()

    assert len(actual) == len(expected_output)
    for i, expected_entry in enumerate(expected_output):
        assert actual[i]["z_index"] == i
        assert actual[i]["frame_acquisition_order"] == expected_entry[0]
        assert actual[i]["raw_angle"] == expected_entry[1]
        assert actual[i]["astigmatic_angle"] is None
        assert actual[i]["major_defocus"] is None
        assert actual[i]["max_resolution"] is None
        assert actual[i]["minor_defocus"] is None
        assert actual[i]["phase_shift"] is None
