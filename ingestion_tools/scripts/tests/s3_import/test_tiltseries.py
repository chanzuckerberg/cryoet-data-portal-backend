import json
import os.path
from typing import Callable

import pytest as pytest
from importers.tiltseries import TiltSeriesImporter
from mypy_boto3_s3 import S3Client

from common.fs import FileSystemApi
from tests.s3_import.test_per_section_parameter import expected_psp_output, setup_psp_generator
from tests.s3_import.util import (
    create_config,
    get_children,
    get_data_from_s3,
    get_raw_data_from_s3,
    get_run_and_parents,
)


@pytest.fixture
def validate_metadata(s3_client: S3Client, test_output_bucket: str) -> Callable[[dict, str, int], None]:
    def validate(expected: dict, prefix: str) -> None:
        key = os.path.join(prefix, "tiltseries_metadata.json")
        actual = json.loads(get_data_from_s3(s3_client, test_output_bucket, key).read())
        content_type = get_raw_data_from_s3(s3_client, test_output_bucket, key)["ContentType"]

        for k in expected:
            assert actual[k] == expected[k], f"Key {k} does not match"
        assert content_type == "application/json"

    return validate


@pytest.fixture
def add_tiltseries_metadata(s3_client: S3Client, test_output_bucket: str) -> Callable[[str, int], None]:
    def _add_tiltseries_metadata(prefix: str, deposition_id: int) -> None:
        body = json.dumps({"deposition_id": deposition_id}).encode("utf-8")
        key = os.path.join(prefix, "100", "tiltseries_metadata.json")
        s3_client.put_object(Bucket=test_output_bucket, Key=key, Body=body)

    return _add_tiltseries_metadata


@pytest.mark.parametrize(
    "deposition_id, id_prefix",
    [
        (None, 100),  # No tiltseries metadata exists
        (100001, 101),  # tiltseries metadata exists for a different deposition
        (10301, 100),  # tiltseries metadata exists for the same deposition as test
    ],
    ids=["no_metadata_exists", "metadata_with_different_dep_id_exists", "metadata_with_same_dep_id"],
)
def test_tiltseries_import(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    s3_client: S3Client,
    add_tiltseries_metadata: Callable[[str, int], None],
    validate_metadata: Callable[[dict, str, int], None],
    deposition_id: int,
    id_prefix: int,
) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_run_and_parents(config)
    run_name = parents["run"].name
    prefix = f"output/{parents['dataset'].name}/{run_name}/TiltSeries/"
    if deposition_id:
        add_tiltseries_metadata(prefix, deposition_id)

    tilt_series = list(TiltSeriesImporter.finder(config, **parents))
    for item in tilt_series:
        item.import_item()
        setup_psp_generator(config, {**parents, "tiltseries": item})
        item.import_metadata()
    output_prefix = os.path.join(prefix, str(id_prefix))
    tilt_series_files = get_children(s3_client, test_output_bucket, output_prefix)
    assert f"{run_name}.mrc" in tilt_series_files
    assert f"{run_name}.zarr" in tilt_series_files
    assert "tiltseries_metadata.json" in tilt_series_files


@pytest.mark.parametrize(
    "config_path, expected_pixel_spacing, expected_frames_count, expected_ctf_path, expected_psp",
    [
        # pixel_spacing is present in metadata
        ("dataset1.yaml", 3.3702, 5, "10001/TS_run1/TiltSeries/100/TS_run1_CTFFIND_ctf.txt", expected_psp_output(True)),
        # pixel_spacing is fetched from the mrc file
        ("tiltseries/test1.yaml", 5.678, 0, None, expected_psp_output(False)),
    ],
    ids=["valid_pixel_spacing_in_metadata", "pixel_spacing_from_volume"],
)
def test_tiltseries_import_metadata(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    s3_client: S3Client,
    validate_metadata: Callable[[dict, str], None],
    config_path: str,
    expected_pixel_spacing: float,
    expected_frames_count: int,
    expected_ctf_path: str,
    expected_psp: list[dict],
) -> None:
    """
    To recreate the test mrc file with the dimensions and pixel spacing used in the test, use create_mrc method in
    data_generators.generate_data.py
    python generate_data.py create-mrc ../../../../test_infra/test_files/input_bucket/10001_input/metadata/TS_run1.st \
    --size 4,10,20 --voxel-spacing 5.678
    """
    config = create_config(s3_fs, test_output_bucket, config_path=config_path)
    parents = get_run_and_parents(config)

    tilt_series = list(TiltSeriesImporter.finder(config, **parents))
    for item in tilt_series:
        item.import_item()
        setup_psp_generator(config, {**parents, "tiltseries": item})
        item.import_metadata()

    run_name = parents["run"].name
    prefix = f"output/{parents['dataset'].name}/{run_name}/TiltSeries/100"
    tilt_series_files = get_children(s3_client, test_output_bucket, prefix)
    assert "tiltseries_metadata.json" in tilt_series_files
    expected = {
        "frames_count": expected_frames_count,
        "omezarr_dir": f"{parents['dataset'].name}/{run_name}/TiltSeries/100/{run_name}.zarr",
        "mrc_file": f"{parents['dataset'].name}/{run_name}/TiltSeries/100/{run_name}.mrc",
        "pixel_spacing": expected_pixel_spacing,
        "scales": [{"z": 4, "y": 10, "x": 20}, {"z": 4, "y": 5, "x": 10}, {"z": 4, "y": 3, "x": 5}],
        "size": {"z": 4, "y": 10, "x": 20},
        "raw_tlt_path": f"{parents['dataset'].name}/{run_name}/TiltSeries/100/TS_run1.rawtlt",
        "ctf_path": expected_ctf_path,
        "per_section_parameter": expected_psp,
    }
    validate_metadata(expected, prefix)

def test_tiltseries_no_import(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    s3_client: S3Client,
) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_run_and_parents(config)
    tilt_series = list(TiltSeriesImporter.finder(config, **parents))
    for item in tilt_series:
        item.allow_imports = False
        item.import_item()
        item.import_metadata()
    prefix = f"output/{parents['dataset'].name}/{parents['run'].name}/TiltSeries"
    assert set() == get_children(s3_client, test_output_bucket, prefix)
