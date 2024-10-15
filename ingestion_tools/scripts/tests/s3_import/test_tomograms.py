import json
import os.path
from typing import Callable

import pytest as pytest
from importers.base_importer import BaseImporter
from importers.tomogram import TomogramImporter
from importers.voxel_spacing import VoxelSpacingImporter
from mypy_boto3_s3 import S3Client

from common.config import DepositionImportConfig
from common.fs import FileSystemApi
from tests.s3_import.util import create_config, get_children, get_data_from_s3, get_run_and_parents


@pytest.fixture
def validate_metadata(s3_client: S3Client, test_output_bucket: str) -> Callable[[dict, str, int], None]:
    def validate(expected: dict, prefix: str) -> None:
        key = os.path.join(prefix, "tomogram_metadata.json")
        actual = json.loads(get_data_from_s3(s3_client, test_output_bucket, key).read())
        for key in expected:
            assert actual[key] == expected[key], f"Key {key} does not match"

    return validate


@pytest.fixture
def add_tomogram_metadata(s3_client: S3Client, test_output_bucket: str) -> Callable[[str, int], None]:
    def _add_tomogram_metadata(prefix: str, deposition_id: int, additional_metadata: dict = None) -> None:
        data = {"deposition_id": deposition_id}
        if additional_metadata:
            data.update(additional_metadata)
        body = json.dumps(data).encode("utf-8")
        key = os.path.join(prefix, "100", "tomogram_metadata.json")
        s3_client.put_object(Bucket=test_output_bucket, Key=key, Body=body)

    return _add_tomogram_metadata


def get_parents(config: DepositionImportConfig) -> dict[str, BaseImporter]:
    parents = get_run_and_parents(config)
    parents["voxel_spacing"] = list(VoxelSpacingImporter.finder(config, **parents))[0]
    return parents


@pytest.mark.parametrize(
    "deposition_id, existing_metadata, alignment_path, id_prefix",
    [
        (None, None, None, 100),  # No tomogram metadata exists # tomogram metadata exists for a different deposition
        (
            10301,
            {"reconstruction_method": "WBP", "processing": "raw"},
            None,
            100,
        ),  # tomogram metadata exists for the same deposition as test
        (
            10301,
            {"reconstruction_method": "WBP", "processing": "raw"},
            "100/alignment_metadata.json",
            100,
        ),  # tomogram metadata exists for the same deposition and alignment path specified in metadata
        (
            100001,
            {"reconstruction_method": "WBP", "processing": "raw"},
            "100/alignment_metadata.json",
            101,
        ),  # Existing metadata has same values other than deposition id and alignment path is specified in metadata
        (
            100001,
            {"reconstruction_method": "WBP", "processing": "raw"},
            None,
            101,
        ),  # Existing metadata with different deposition_id and alignment defaulting to tomogram's alignment
        (
            10301,
            {"reconstruction_method": "WBP", "processing": "raw"},
            "foo.json",
            101,
        ),  # Existing metadata with same deposition_id but different alignment path
        (
            10301,
            {"reconstruction_method": "SIRT", "processing": "raw"},
            "100/alignment_metadata.json",
            101,
        ),  # Existing metadata with same deposition_id but different reconstruction_method
        (
            10301,
            {"reconstruction_method": "WBP", "processing": "denoised"},
            "100/alignment_metadata.json",
            101,
        ),  # Existing metadata with same deposition_id but different processing
        (
            10301,
            {"reconstruction_method": "WBP", "processing": "raw", "voxel_spacing": 20},
            "100/alignment_metadata.json",
            101,
        ),  # Existing metadata with same deposition_id but different voxel_spacing
    ],
)
def test_tomogram_import(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    s3_client: S3Client,
    add_tomogram_metadata: Callable[[str, int, dict], None],
    validate_metadata: Callable[[dict, str], None],
    deposition_id: int,
    existing_metadata: dict,
    alignment_path: str,
    id_prefix: int,
) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_parents(config)
    run_name = parents["run"].name
    voxel_spacing = 13.48
    prefix = f"output/{parents['dataset'].name}/{run_name}/Reconstructions/VoxelSpacing{{voxel_spacing:.3f}}/Tomograms"
    if deposition_id and existing_metadata:
        if alignment_path:
            existing_metadata["alignment_metadata_path"] = os.path.join(
                f"{parents['dataset'].name}/{run_name}/Alignments", alignment_path,
            )
        existing_prefix = prefix.format(voxel_spacing=existing_metadata.get("voxel_spacing", voxel_spacing))
        add_tomogram_metadata(existing_prefix, deposition_id, existing_metadata)

    tomogram = list(TomogramImporter.finder(config, **parents))
    for item in tomogram:
        item.import_item()
        item.import_metadata()
    prefix = prefix.format(voxel_spacing=voxel_spacing)
    tomogram_files = get_children(s3_client, test_output_bucket, os.path.join(prefix, str(id_prefix)))
    assert f"{run_name}.mrc" in tomogram_files
    assert f"{run_name}.zarr" in tomogram_files
    assert "tomogram_metadata.json" in tomogram_files


def test_tomogram_import_metadata(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    s3_client: S3Client,
    validate_metadata: Callable[[dict, str], None],
) -> None:
    """
    To recreate the test mrc file with the dimensions and pixel spacing used in the test, use create_mrc method in
    data_generators.generate_data.py
    python generate_data.py create-mrc ../../../../test_infra/test_files/input_bucket/10001_input/tomograms/TS_run1.rec \
    --size 10,8,6 --voxel-spacing 13.480
    """
    config = create_config(s3_fs, test_output_bucket)
    parents = get_parents(config)
    tomogram = list(TomogramImporter.finder(config, **parents))
    for item in tomogram:
        item.import_item()
        item.import_metadata()
    run_name = parents["run"].name
    voxel_spacing = 13.48
    vs_path = f"{parents['dataset'].name}/{run_name}/Reconstructions/VoxelSpacing{voxel_spacing:.3f}"
    id_prefix = 100
    prefix = f"{vs_path}/Tomograms/{id_prefix}"
    tomogram_files = get_children(s3_client, test_output_bucket,  f"output/{prefix}")
    assert "tomogram_metadata.json" in tomogram_files
    image_path = f"{vs_path}/Images/{id_prefix}/key-photo-"
    expected = {
        "omezarr_dir": os.path.join(prefix, f"{run_name}.zarr"),
        "mrc_file": os.path.join(prefix, f"{run_name}.mrc"),
        "voxel_spacing": 13.48,
        "scales": [{"x": 6, "y": 8, "z": 10}, {"x": 3, "y": 4, "z": 5}, {"x": 2, "y": 2, "z": 3}],
        "size": {"x": 6, "y": 8, "z": 10},
        "alignment_metadata_path": f"{parents['dataset'].name}/{run_name}/Alignments/100/alignment_metadata.json",
        "neuroglancer_config_path": f"{vs_path}/NeuroglancerPrecompute/"
                                    f"{id_prefix}-neuroglancer_config.json",
        "key_photo": {
            "snapshot": f"{image_path}snapshot.png",
            "thumbnail": f"{image_path}thumbnail.png",
        },
    }
    validate_metadata(expected, f"output/{prefix}")


def test_tomogram_no_import(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    s3_client: S3Client,
) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_parents(config)
    tomogram = list(TomogramImporter.finder(config, **parents))
    for item in tomogram:
        item.allow_imports = False
        item.import_item()
        item.import_metadata()
    prefix = f"output/{parents['dataset'].name}/{parents['run'].name}/Reconstructions"
    assert set() == get_children(s3_client, test_output_bucket, prefix)
