import pytest
from importers.base_importer import BaseImporter
from importers.collection_metadata import CollectionMetadataImporter
from importers.ctf import CtfImporter
from importers.rawtilt import RawTiltImporter
from importers.tiltseries import PerSectionParameterGenerator, TiltSeriesImporter
from mypy_boto3_s3 import S3Client

from common.config import DepositionImportConfig
from common.fs import FileSystemApi
from tests.s3_import.util import create_config, get_run_and_parents


def expected_psp_output(has_ctf: bool) -> list[dict]:
    expected_values = [
        (3, -4.38, None, None, None, None, None, None),
        (2, -1.98, -46.02, 3.0, 45.0, -46.02, 3574.0, 3329.0),
        (0, -0.00499939, -52.02, 1.0, 60.0, -52.02, 3345.0, 3328.0),
        (1, 2.013, -49.02, 2.0, 19.0, -49.02, 3309.0, 3095.0),
    ]
    return [
        {
            "z_index": i,
            "frame_acquisition_order": entry[0],
            "raw_angle": entry[1],
            "astigmatic_angle": entry[2] if has_ctf else None,
            "major_defocus": entry[3] if has_ctf else None,
            "max_resolution": entry[4] if has_ctf else None,
            "minor_defocus": entry[5] if has_ctf else None,
            "phase_shift": entry[6] if has_ctf else None,
            "cross_correlation": entry[7] if has_ctf else None,
        }
        for i, entry in enumerate(expected_values)
    ]


def get_parents(config: DepositionImportConfig) -> dict[str, BaseImporter]:
    parents = get_run_and_parents(config)
    parents["tiltseries"] = next(TiltSeriesImporter.finder(config, **parents))
    return parents


def setup_psp_generator(config: DepositionImportConfig, parents: dict[str, BaseImporter]) -> None:
    for mdoc_importer in CollectionMetadataImporter.finder(config, **parents):
        mdoc_importer.import_item()

    for raw_tlt_importer in RawTiltImporter.finder(config, **parents):
        raw_tlt_importer.import_item()

    for ctf_importer in CtfImporter.finder(config, **parents):
        ctf_importer.import_item()


def test_psp_success(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_parents(config)
    setup_psp_generator(config, parents)

    psp_generator = PerSectionParameterGenerator(config, parents)
    ds_name = parents["dataset"].name
    run_name = parents["run"].name
    assert f"{ds_name}/{run_name}/TiltSeries/100/TS_run1.rawtlt" == psp_generator.get_raw_tlt_path()
    assert f"{ds_name}/{run_name}/TiltSeries/100/TS_run1_ctffind4.txt" == psp_generator.get_ctf_path()
    actual = psp_generator.get_data()
    expected_output = expected_psp_output(True)
    assert len(actual) == len(expected_output)
    assert actual == expected_output

def test_psp_close_tilt_angles(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    """
    Test the PerSectionParameterGenerator with a configuration that uses tilt angles that are within 0.1 degrees of each other,
    an uncommon case that should still be handled correctly.
    """
    config = create_config(s3_fs, test_output_bucket, "tiltseries/close_tilt_angles_mdoc_rawtlt.yaml")
    parents = get_parents(config)
    setup_psp_generator(config, parents)

    psp_generator = PerSectionParameterGenerator(config, parents)
    actual = psp_generator.get_data()
    expected_output = expected_psp_output(True)
    assert actual == expected_output

def test_psp_no_mdoc(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_parents(config)
    config.object_configs.pop("collection_metadata")
    setup_psp_generator(config, parents)

    with pytest.raises(FileNotFoundError):
        psp_generator = PerSectionParameterGenerator(config, parents)
        psp_generator.get_data()


def test_psp_no_rawtilt(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_parents(config)
    config.object_configs.pop("rawtilt")
    setup_psp_generator(config, parents)

    with pytest.raises(FileNotFoundError):
        PerSectionParameterGenerator(config, parents)


def test_psp_mdoc_rawtlt_mismatch(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config = create_config(s3_fs, test_output_bucket, "tiltseries/invalid_mdoc_rawtlt.yaml")
    parents = get_parents(config)
    setup_psp_generator(config, parents)

    psp_generator = PerSectionParameterGenerator(config, parents)

    with pytest.raises(KeyError):
        psp_generator.get_data()


def test_psp_no_ctf(
        s3_fs: FileSystemApi,
        test_output_bucket: str,
        s3_client: S3Client,
) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_parents(config)
    config.object_configs.pop("ctf")
    setup_psp_generator(config, parents)

    psp_generator = PerSectionParameterGenerator(config, parents)
    actual = psp_generator.get_data()

    ds_name = parents["dataset"].name
    run_name = parents["run"].name
    assert f"{ds_name}/{run_name}/TiltSeries/100/TS_run1.rawtlt" == psp_generator.get_raw_tlt_path()
    assert psp_generator.get_ctf_path() is None
    expected_output = expected_psp_output(False)
    assert len(actual) == len(expected_output)
    assert actual == expected_output
