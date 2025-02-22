import json
import os.path
from typing import Callable

import pytest
from importers.collection_metadata import CollectionMetadataImporter
from importers.frame import FrameImporter
from mypy_boto3_s3 import S3Client

from common.fs import FileSystemApi
from tests.s3_import.util import (
    create_config,
    get_children,
    get_raw_data_from_s3,
    get_run_and_parents,
    list_dir,
    validate_output_data_is_same_as_source,
)

VALID_FRAMES_METADATA = [
    (1.881 * 1, "TS_run1_1.tiff"),
    (1.881 * 1.58, "TS_run1_2.tiff"),
    (1.881 * 1.59, "TS_run1_3.tiff"),
    (1.881 * 1.58, "TS_run1_4.tiff"),
    (1.881 * 1.58, "TS_run1_5.tiff"),
]
DEFAULT_FRAMES_METADATA = [
    (1.881 * 1, None),
    (1.881 * 1.58, None),
    (1.881 * 1.59, None),
    (1.881 * 1.58, None),
    (1.881 * 1.58, None),
]

def generate_expected_metadata(
        input_values: list[tuple[float, str|None]],
        is_gain_corrected: bool | None,
        mdoc_file_name: str,
        frame_path: str,
) -> dict:
    frames = []
    accumulated_dose = 0
    for index, entry in enumerate(input_values):
        item = {
            "acquisition_order": index,
            "accumulated_dose": accumulated_dose,
            "exposure_dose": entry[0],
            "is_gain_corrected": is_gain_corrected,
            "path": os.path.join(frame_path, entry[1]) if entry[1] else None,
        }
        accumulated_dose += entry[0]
        frames.append(item)
    return {
        "frames_acquisition_file": f"{frame_path}/{mdoc_file_name}",
        "frames": frames,
    }

@pytest.fixture
def validate_metadata(s3_client: S3Client, test_output_bucket: str) -> Callable[[dict, str, int], None]:
    def validate(expected: dict, prefix: str) -> None:
        key = os.path.join(prefix, "frames_metadata.json")
        raw_data = get_raw_data_from_s3(s3_client, test_output_bucket, key)
        assert raw_data["ContentType"] == "application/json"
        actual = json.loads(raw_data["Body"].read())
        for k in expected:
            assert actual[k] == expected[k], f"Key {k} does not match"

    return validate


def test_frames_import(
        s3_fs: FileSystemApi,
        test_output_bucket: str,
        s3_client: S3Client,
        validate_metadata: Callable[[dict, str, int], None],
) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_run_and_parents(config)

    for item in CollectionMetadataImporter.finder(config, **parents):
        item.import_item()

    frames_importer = list(FrameImporter.finder(config, **parents))[0]
    frames_importer.import_item()
    frames_importer.import_metadata()

    run_name = parents["run"].name
    frame_path = f"{parents['dataset'].name}/{run_name}/Frames"
    prefix = f"output/{frame_path}"
    validate_output_data_is_same_as_source(s3_client, test_output_bucket, prefix, frames_importer)
    expected_metadata = generate_expected_metadata(VALID_FRAMES_METADATA, True,"foo-TS_run1.mdoc", frame_path)
    validate_metadata(expected_metadata, prefix)


def test_frames_default_import(
        s3_fs: FileSystemApi,
        test_output_bucket: str,
        s3_client: S3Client,
        validate_metadata: Callable[[dict, str, int], None],
) -> None:
    config = create_config(s3_fs, test_output_bucket, "frames/default.yaml")
    parents = get_run_and_parents(config)

    for item in CollectionMetadataImporter.finder(config, **parents):
        item.import_item()

    frames_importer = list(FrameImporter.finder(config, **parents))[0]
    frames_importer.import_item()
    frames_importer.import_metadata()

    run_name = parents["run"].name
    frame_path = f"{parents['dataset'].name}/{run_name}/Frames"
    prefix = f"output/{frame_path}"
    assert {"foo-TS_run1.mdoc", "frames_metadata.json"} == get_children(s3_client, test_output_bucket, prefix)
    expected_metadata = generate_expected_metadata(DEFAULT_FRAMES_METADATA, None,"foo-TS_run1.mdoc", frame_path)
    validate_metadata(expected_metadata, prefix)

def test_frames_invalid_import(
        s3_fs: FileSystemApi,
        test_output_bucket: str,
        s3_client: S3Client,
        validate_metadata: Callable[[dict, str, int], None],
) -> None:
    config = create_config(s3_fs, test_output_bucket, "frames/default.yaml")
    config.object_configs["frame"][0]["metadata"].pop("dose_rate") #Deleting required field
    parents = get_run_and_parents(config)

    for item in CollectionMetadataImporter.finder(config, **parents):
        item.import_item()

    frames_importer = list(FrameImporter.finder(config, **parents))[0]
    frames_importer.import_item()

    with pytest.raises(ValueError):
        frames_importer.import_metadata()

    run_name = parents["run"].name
    frame_path = f"{parents['dataset'].name}/{run_name}/Frames"
    prefix = f"output/{frame_path}"
    assert {"foo-TS_run1.mdoc"} == get_children(s3_client, test_output_bucket, prefix)


def test_frames_no_import(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config = create_config(s3_fs, test_output_bucket)
    parents = get_run_and_parents(config)

    frames_importer = list(FrameImporter.finder(config, **parents))[0]
    frames_importer.allow_imports = False
    frames_importer.import_item()
    frames_importer.import_metadata()

    prefix = f"output/{parents['dataset'].name}/{parents['run'].name}/Frames"
    actual_files = [os.path.basename(item) for item in list_dir(s3_client, test_output_bucket, prefix)]
    assert actual_files == []
