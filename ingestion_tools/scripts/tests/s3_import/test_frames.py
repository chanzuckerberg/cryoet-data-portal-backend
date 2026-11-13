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
    create_config_with_mdoc,
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
    expected_metadata = generate_expected_metadata(VALID_FRAMES_METADATA, True,"TS_run1.mdoc", frame_path)
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
    assert {"TS_run1.mdoc", "frames_metadata.json"} == get_children(s3_client, test_output_bucket, prefix)
    expected_metadata = generate_expected_metadata(DEFAULT_FRAMES_METADATA, None,"TS_run1.mdoc", frame_path)
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
    assert {"TS_run1.mdoc"} == get_children(s3_client, test_output_bucket, prefix)


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


# The mdoc fixture "anglesorted" lists the sections of TS_run1.mdoc sorted by tilt angle with ZValue renumbered
# (as e.g. PACEtomo writes it); its DateTimes give the true acquisition order, which is the order of TS_run1.mdoc.
ANGLE_SORTED_FRAMES_METADATA = [
    (1.881 * 1.58, "TS_run1_4.tiff"),
    (1.881 * 1.59, "TS_run1_3.tiff"),
    (1.881 * 1, "TS_run1_1.tiff"),
    (1.881 * 1.58, "TS_run1_2.tiff"),
    (1.881 * 1.58, "TS_run1_5.tiff"),
]


def import_frames_metadata(config) -> tuple[FrameImporter, str]:
    parents = get_run_and_parents(config)
    for item in CollectionMetadataImporter.finder(config, **parents):
        item.import_item()
    frames_importer = list(FrameImporter.finder(config, **parents))[0]
    frames_importer.import_item()
    frames_importer.import_metadata()
    return frames_importer, f"{parents['dataset'].name}/{parents['run'].name}/Frames"


@pytest.mark.parametrize(
    "mdoc_prefix, options",
    [
        ("anglesorted", {"acquisition_order_from_datetime": True}),
        # newer SerialEM versions write a four-digit year
        ("anglesorted-4digit-year", {"acquisition_order_from_datetime": True}),
        ("anglesorted-iso", {"acquisition_order_from_datetime": True, "datetime_format": "%Y-%m-%dT%H:%M:%S"}),
    ],
)
def test_frames_acquisition_order_from_datetime(
        s3_fs: FileSystemApi,
        test_output_bucket: str,
        validate_metadata: Callable[[dict, str, int], None],
        mdoc_prefix: str,
        options: dict,
) -> None:
    """With acquisition_order_from_datetime, an angle-sorted mdoc gives the same frames as the time-ordered one."""
    config = create_config_with_mdoc(s3_fs, test_output_bucket, mdoc_prefix, options)
    _, frame_path = import_frames_metadata(config)

    expected_metadata = generate_expected_metadata(VALID_FRAMES_METADATA, True, "TS_run1.mdoc", frame_path)
    validate_metadata(expected_metadata, f"output/{frame_path}")


@pytest.mark.parametrize("options", [None, {"acquisition_order_from_datetime": False}])
def test_frames_angle_sorted_mdoc_defaults_to_zvalue(
        s3_fs: FileSystemApi,
        test_output_bucket: str,
        validate_metadata: Callable[[dict, str, int], None],
        capsys: pytest.CaptureFixture,
        options: dict | None,
) -> None:
    """Without the option, acquisition order stays ZValue (file order), but the mismatch is reported."""
    config = create_config_with_mdoc(s3_fs, test_output_bucket, "anglesorted", options)
    _, frame_path = import_frames_metadata(config)

    expected_metadata = generate_expected_metadata(ANGLE_SORTED_FRAMES_METADATA, True, "TS_run1.mdoc", frame_path)
    validate_metadata(expected_metadata, f"output/{frame_path}")
    assert "are not in DateTime order" in capsys.readouterr().out


@pytest.mark.parametrize(
    "mdoc_prefix, options",
    [
        # the option is set, so the order already follows DateTime
        ("anglesorted", {"acquisition_order_from_datetime": True}),
        # the default mdoc is in acquisition order (and has a single DateTime)
        ("foo", None),
    ],
)
def test_frames_no_datetime_order_warning(
        s3_fs: FileSystemApi,
        test_output_bucket: str,
        capsys: pytest.CaptureFixture,
        mdoc_prefix: str,
        options: dict | None,
) -> None:
    config = create_config_with_mdoc(s3_fs, test_output_bucket, mdoc_prefix, options)
    import_frames_metadata(config)
    assert "are not in DateTime order" not in capsys.readouterr().out


@pytest.mark.parametrize(
    "mdoc_prefix, options, message",
    [
        # ISO DateTimes don't match the default SerialEM format
        ("anglesorted-iso", {"acquisition_order_from_datetime": True}, "doesn't match the format"),
        ("anglesorted", {"acquisition_order_from_datetime": True, "datetime_format": "%Y"}, "doesn't match the format"),
        ("anglesorted-duplicate-datetime", {"acquisition_order_from_datetime": True}, "share a DateTime"),
        # no DateTime at all
        ("foo", {"acquisition_order_from_datetime": True}, "missing"),
    ],
)
def test_frames_acquisition_order_from_datetime_invalid(
        s3_fs: FileSystemApi, test_output_bucket: str, mdoc_prefix: str, options: dict, message: str,
) -> None:
    config = create_config_with_mdoc(s3_fs, test_output_bucket, mdoc_prefix, options)
    with pytest.raises(ValueError, match=message):
        import_frames_metadata(config)
