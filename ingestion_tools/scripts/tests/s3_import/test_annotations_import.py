import json
from os.path import basename
from typing import Any, Dict, List

import ndjson
import pytest
from importers.annotation import PointAnnotation, OrientedPointAnnotation, InstanceSegmentationAnnotation
from importers.dataset import DatasetImporter
from importers.run import RunImporter
from importers.tomogram import TomogramImporter
from importers.voxel_spacing import VoxelSpacingImporter
from mypy_boto3_s3 import S3Client
from standardize_dirs import IMPORTERS

from common.config import DepositionImportConfig
from common.fs import FileSystemApi

default_anno_metadata = {
    "annotation_object": {
        "id": "GO:0001234",
        "name": "some protein",
        "description": "some protein",
    },
    "dates": {
        "deposition_date": "2022-02-02",
        "release_date": "2022-02-02",
        "last_modified": "2022-02-02",
    },
    "annotation_method": "manual annotation",
    "method_type": "hybrid",
    "annotation_publications": "EMPIAR-12345",
    "ground_truth_status": True,
    "authors": [{"name": "Author 1", "ORCID": "0000-0000-0000-0000", "primary_author_status": True}],
    "annotation_software": "pyTOM + Keras",
    "version": "1.0",
    "is_curator_recommended": True,
}

NUMERICAL_PRECISION = 1e-8


@pytest.fixture
def dataset_config(s3_fs: FileSystemApi, test_output_bucket: str) -> DepositionImportConfig:
    config_file = "tests/fixtures/annotations/anno_config.yaml"
    output_path = f"{test_output_bucket}/output"
    input_bucket = "test-public-bucket"
    config = DepositionImportConfig(s3_fs, config_file, output_path, input_bucket, IMPORTERS)
    return config


@pytest.fixture
def tomo_importer(dataset_config: DepositionImportConfig) -> TomogramImporter:
    dataset = DatasetImporter(config=dataset_config, metadata={}, name="dataset1", path="dataset1")
    run = RunImporter(config=dataset_config, metadata={}, name="run1", path="run1", parents={"dataset": dataset})
    vs = VoxelSpacingImporter(config=dataset_config, metadata={}, name="10.0", path="vs1", parents={"dataset": dataset, "run": run})
    tomo = TomogramImporter(config=dataset_config, metadata={}, name="tomo1", path="run1", parents={"dataset": dataset, "run": run, "voxel_spacing": vs})
    return tomo


def list_dir(s3_client: S3Client, bucket: str, prefix: str) -> List[str]:
    files = s3_client.list_objects(Bucket=bucket, Prefix=prefix)
    fnames = []
    for item in files["Contents"]:
        fnames.append(item["Key"])
    return fnames


def test_import_annotation_metadata(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    tomo_importer: TomogramImporter,
    dataset_config: DepositionImportConfig,
    s3_client: S3Client,
) -> None:
    anno_config = {
        "metadata": default_anno_metadata,
        "sources": [{
            "file_format": "csv",
            "delimiter": ",",
            "shape": "Point",
            "glob_string": "annotations/*.csv",
            "columns": "xyz",
        }]
    }
    dataset_config._set_object_configs("annotation", [anno_config])

    anno = PointAnnotation(
        config=dataset_config,
        metadata=default_anno_metadata,
        path="test-public-bucket/input_bucket/20002/annotations/points.csv",
        parents={"tomogram": tomo_importer, **tomo_importer.parents},
        identifier=100,
        columns=anno_config["sources"][0].get("columns"),
        delimiter=anno_config["sources"][0].get("delimiter"),
        file_format=anno_config["sources"][0]["file_format"],
    )
    anno.import_item()
    anno.import_metadata()

    # Strip the bucket name and annotation name from the annotation's output path.
    prefix = anno.get_output_path().rsplit("/", 1)[0].split("/", 1)[1]
    metadata_file = anno.get_output_path() + ".json"
    anno_file = anno.get_output_path() + "_point.ndjson"
    # Make sure we have a ndjson data file and a metadata file
    anno_files = [basename(item) for item in list_dir(s3_client, test_output_bucket, prefix)]
    assert "100-some_protein-1.0.json" in anno_files
    assert "100-some_protein-1.0_point.ndjson" in anno_files

    # Sanity check the metadata
    with s3_fs.open(metadata_file, "r") as fh:
        metadata = json.load(fh)
    assert metadata["annotation_object"] == default_anno_metadata["annotation_object"]
    assert metadata["annotation_software"] == default_anno_metadata["annotation_software"]
    assert metadata["object_count"] == 3
    fileinfo = metadata["files"][0]
    assert fileinfo["format"] == "ndjson"
    assert fileinfo["shape"] == "Point"
    assert "100-some_protein-1.0_point.ndjson" in fileinfo["path"]

    # Sanity check the ndjson file
    with s3_fs.open(anno_file, "r") as fh:
        points = ndjson.load(fh)
    assert len(points) == 3

ingest_points_test_cases = [
    # csv
    {
        "case": "csv, comma delimiter, binning 1",
        "source_cfg": {
            "columns": "xyz",
            "file_format": "csv",
            "glob_string": "annotations/points.csv",
            "shape": "Point",
            "is_visualization_default": False,
        },
        "count": 3,
        "out_data": [
            {"type": "point", "location": {"x": 1, "y": 2, "z": 3}},
            {"type": "point", "location": {"x": 2, "y": 2, "z": 2}},
            {"type": "point", "location": {"x": 0, "y": 3, "z": 0}},
        ],
    },
    {
        "case": "csv, tab delimiter, binning 2",
        "source_cfg": {
            "columns": "xyz",
            "file_format": "csv",
            "glob_string": "annotations/points_tab_delim.csv",
            "shape": "Point",
            "is_visualization_default": False,
            "binning": 2,
            "delimiter": "\t",
        },
        "count": 3,
        "out_data": [
            {"type": "point", "location": {"x": 0.5, "y": 1, "z": 1.5}},
            {"type": "point", "location": {"x": 1, "y": 1, "z": 1}},
            {"type": "point", "location": {"x": 0, "y": 1.5, "z": 0}},
        ],
    },
    # csv_with_header
    {
        "case": "csv_with_header, comma delimiter, binning 1",
        "source_cfg": {
            "columns": "xyz",
            "file_format": "csv_with_header",
            "glob_string": "annotations/points_with_header.csv",
            "shape": "Point",
            "is_visualization_default": False,
        },
        "count": 3,
        "out_data": [
            {"type": "point", "location": {"x": 1, "y": 2, "z": 3}},
            {"type": "point", "location": {"x": 2, "y": 2, "z": 2}},
            {"type": "point", "location": {"x": 0, "y": 3, "z": 0}},
        ],
    },
    {
        "case": "csv_with_header, pipe delimiter, binning 2",
        "source_cfg": {
            "columns": "xyz",
            "file_format": "csv_with_header",
            "glob_string": "annotations/points_with_header_pipe_delim.csv",
            "shape": "Point",
            "is_visualization_default": False,
            "binning": 2,
            "delimiter": "|",
        },
        "count": 3,
        "out_data": [
            {"type": "point", "location": {"x": 0.5, "y": 1, "z": 1.5}},
            {"type": "point", "location": {"x": 1, "y": 1, "z": 1}},
            {"type": "point", "location": {"x": 0, "y": 1.5, "z": 0}},
        ],
    },
    # IMOD mod
    {
        "case": "mod, binning 2",
        "source_cfg": {
            "file_format": "mod",
            "glob_string": "annotations/points.mod",
            "shape": "Point",
            "is_visualization_default": False,
            "binning": 2,
        },
        "count": 3,
        "out_data": [
            {"type": "point", "location": {"x": 0.5, "y": 1, "z": 1.5}},
            {"type": "point", "location": {"x": 1, "y": 1, "z": 1}},
            {"type": "point", "location": {"x": 0, "y": 1.5, "z": 0}},
        ],
    },
]


@pytest.mark.parametrize("case", ingest_points_test_cases)
def test_ingest_point_data(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    tomo_importer: TomogramImporter,
    dataset_config: DepositionImportConfig,
    s3_client: S3Client,
    case: Dict[str, Any],
) -> None:

    # loop through test cases
    anno_config = {
        "metadata": default_anno_metadata,
        "sources": [
            case["source_cfg"],
        ],
    }
    dataset_config._set_object_configs("annotation", [anno_config])

    anno = PointAnnotation(
        config=dataset_config,
        metadata=default_anno_metadata,
        path="test-public-bucket/input_bucket/20002/" + case["source_cfg"]["glob_string"],
        parents={"tomogram": tomo_importer, **tomo_importer.parents},
        identifier=100,
        columns=anno_config["sources"][0].get("columns"),
        delimiter=anno_config["sources"][0].get("delimiter"),
        file_format=anno_config["sources"][0]["file_format"],
        binning=anno_config["sources"][0].get("binning"),
    )
    anno.import_item()

    # Strip the bucket name and annotation name from the annotation's output path.
    anno_file = anno.get_output_filename(anno.get_output_path())

    # Sanity check the ndjson file
    with s3_fs.open(anno_file, "r") as fh:
        points = ndjson.load(fh)

    # Check length of points
    assert len(points) == case["count"], f"Incorrect number of points for {case['case']}"

    # Check data
    for point, exp_point in zip(points, case["out_data"], strict=True):
        # Type
        assert exp_point["type"] == point["type"], f"Incorrect point type for {case['case']}"

        # Location with specified numerical precision
        loc = point["location"]
        exp_loc = exp_point["location"]
        for dim in ["x", "y", "z"]:
            assert loc[dim] == pytest.approx(
                exp_loc[dim],
                abs=NUMERICAL_PRECISION,
            ), f"Incorrect point data for {case['case']}"


ingest_oriented_points_test_cases = [
    # relion3_star
    {
        "case": "relion3_star, filter value 1, binning 4",
        "source_cfg": {
            "order": "xyz",
            "file_format": "relion3_star",
            "glob_string": "annotations/relion_3_star.star",
            "shape": "OrientedPoint",
            "is_visualization_default": False,
            "filter_value": "tomo_1.tomostar",
            "binning": 4,
        },
        "count": 2,
        "out_data": [
            {
                "type": "orientedPoint",
                "location": {"x": 1.3, "y": 2.6, "z": 3.8},
                "rotation_matrix": [
                    [-0.0, 1.0, 0.0],
                    [-0.7071067811865475, -0.0, 0.7071067811865475],
                    [0.7071067811865475, 0.0, 0.7071067811865475],
                ],
            },
            {
                "type": "orientedPoint",
                "location": {"x": 0.2, "y": 0.4, "z": 0.7},
                "rotation_matrix": [
                    [0.6123724356957945, -0.3535533905932737, 0.7071067811865475],
                    [0.6123724356957947, -0.35355339059327356, -0.7071067811865475],
                    [0.4999999999999998, 0.8660254037844386, 0.0],
                ],
            },
        ],
    },
    {
        "case": "relion3_star, filter value 2, binning 2, rotation convention",
        "source_cfg": {
            "order": "xyz",
            "file_format": "relion3_star",
            "glob_string": "annotations/relion_3_star.star",
            "shape": "OrientedPoint",
            "is_visualization_default": False,
            "filter_value": "tomo_2.tomostar",
            "binning": 2,
        },
        "count": 3,
        "out_data": [
            {
                "type": "orientedPoint",
                "location": {"x": 3.5, "y": 3, "z": 2.5},
                "rotation_matrix": [
                    [0, 0.0, 1.0],
                    [0.0, 1.0, 0.0],
                    [-1.0, 0.0, 0],
                ],
            },
            {
                "type": "orientedPoint",
                "location": {"x": -1.5, "y": 2.0, "z": -0.5},
                "rotation_matrix": [
                    [0.6424020199109172, -0.7244443697168013, -0.24999999999999983],
                    [0.5950348471655409, 0.6770771969714244, -0.4330127018922193],
                    [0.48296291314453405, 0.12940952255126045, 0.8660254037844386],
                ],
            },
            {
                "type": "orientedPoint",
                "location": {"x": 4.0, "y": 0.5, "z": 1.0},
                "rotation_matrix": [[0, -0.0, -1.0], [0.0, 1.0, -0.0], [1.0, 0.0, 0]],
            },
        ],
    },
    {
        "case": "relion3_star, filter value 3, binning 1, single point",
        "source_cfg": {
            "order": "xyz",
            "file_format": "relion3_star",
            "glob_string": "annotations/relion_3_star.star",
            "shape": "OrientedPoint",
            "is_visualization_default": False,
            "filter_value": "tomo_3.tomostar",
        },
        "count": 1,
        "out_data": [
            {
                "type": "orientedPoint",
                "location": {"x": 1, "y": 0, "z": -1},
                "rotation_matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            },
        ],
    },
    # tomoman_relion_star
    {
        "case": "tomoman_relion_star, filter value 1, binning 4",
        "source_cfg": {
            "order": "xyz",
            "file_format": "tomoman_relion_star",
            "glob_string": "annotations/tomoman_relion_star.star",
            "shape": "OrientedPoint",
            "is_visualization_default": False,
            "filter_value": "grid_1_lamella1_pos1",
            "binning": 4,
        },
        "count": 2,
        "out_data": [
            {
                "type": "orientedPoint",
                "location": {"x": 1.3, "y": 2.6, "z": 3.8},
                "rotation_matrix": [
                    [-0.0, 1.0, 0.0],
                    [-0.7071067811865475, -0.0, 0.7071067811865475],
                    [0.7071067811865475, 0.0, 0.7071067811865475],
                ],
            },
            {
                "type": "orientedPoint",
                "location": {"x": 0.2, "y": 0.4, "z": 0.7},
                "rotation_matrix": [
                    [0.6123724356957945, -0.3535533905932737, 0.7071067811865475],
                    [0.6123724356957947, -0.35355339059327356, -0.7071067811865475],
                    [0.4999999999999998, 0.8660254037844386, 0.0],
                ],
            },
        ],
    },
    {
        "case": "tomoman_relion_star, filter value 2, binning 2, rotation convention",
        "source_cfg": {
            "order": "xyz",
            "file_format": "tomoman_relion_star",
            "glob_string": "annotations/tomoman_relion_star.star",
            "shape": "OrientedPoint",
            "is_visualization_default": False,
            "filter_value": "grid_1_lamella1_pos2",
            "binning": 2,
        },
        "count": 3,
        "out_data": [
            {
                "type": "orientedPoint",
                "location": {"x": 3.5, "y": 3, "z": 2.5},
                "rotation_matrix": [
                    [0, 0.0, 1.0],
                    [0.0, 1.0, 0.0],
                    [-1.0, 0.0, 0],
                ],
            },
            {
                "type": "orientedPoint",
                "location": {"x": -1.5, "y": 2.0, "z": -0.5},
                "rotation_matrix": [
                    [0.6424020199109172, -0.7244443697168013, -0.24999999999999983],
                    [0.5950348471655409, 0.6770771969714244, -0.4330127018922193],
                    [0.48296291314453405, 0.12940952255126045, 0.8660254037844386],
                ],
            },
            {
                "type": "orientedPoint",
                "location": {"x": 4.0, "y": 0.5, "z": 1.0},
                "rotation_matrix": [[0, -0.0, -1.0], [0.0, 1.0, -0.0], [1.0, 0.0, 0]],
            },
        ],
    },
    {
        "case": "tomoman_relion_star, filter value 3, binning 1, single point",
        "source_cfg": {
            "order": "xyz",
            "file_format": "tomoman_relion_star",
            "glob_string": "annotations/tomoman_relion_star.star",
            "shape": "OrientedPoint",
            "is_visualization_default": False,
            "filter_value": "grid_1_lamella1_pos3",
        },
        "count": 1,
        "out_data": [
            {
                "type": "orientedPoint",
                "location": {"x": 1, "y": 0, "z": -1},
                "rotation_matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            },
        ],
    },
    # relion4_star
    {
        "case": "relion4_star, filter value 1, binning 4",
        "source_cfg": {
            "order": "xyz",
            "file_format": "relion4_star",
            "glob_string": "annotations/relion_4_star.star",
            "shape": "OrientedPoint",
            "is_visualization_default": False,
            "filter_value": "TS_001",
            "binning": 4,
        },
        "count": 2,
        "out_data": [
            {
                "type": "orientedPoint",
                "location": {"x": 1.3, "y": 2.6, "z": 3.8},
                "rotation_matrix": [
                    [-0.0, 1.0, 0.0],
                    [-0.7071067811865475, -0.0, 0.7071067811865475],
                    [0.7071067811865475, 0.0, 0.7071067811865475],
                ],
            },
            {
                "type": "orientedPoint",
                "location": {"x": 0.2, "y": 0.4, "z": 0.7},
                "rotation_matrix": [
                    [0.6123724356957945, -0.3535533905932737, 0.7071067811865475],
                    [0.6123724356957947, -0.35355339059327356, -0.7071067811865475],
                    [0.4999999999999998, 0.8660254037844386, 0.0],
                ],
            },
        ],
    },
    {
        "case": "relion4_star, filter value 2, binning 2, rotation convention",
        "source_cfg": {
            "order": "xyz",
            "file_format": "relion4_star",
            "glob_string": "annotations/relion_4_star.star",
            "shape": "OrientedPoint",
            "is_visualization_default": False,
            "filter_value": "TS_002",
            "binning": 2,
        },
        "count": 3,
        "out_data": [
            {
                "type": "orientedPoint",
                "location": {"x": 3.5, "y": 3, "z": 2.5},
                "rotation_matrix": [
                    [0, 0.0, 1.0],
                    [0.0, 1.0, 0.0],
                    [-1.0, 0.0, 0],
                ],
            },
            {
                "type": "orientedPoint",
                "location": {"x": -1.5, "y": 2.0, "z": -0.5},
                "rotation_matrix": [
                    [0.6424020199109172, -0.7244443697168013, -0.24999999999999983],
                    [0.5950348471655409, 0.6770771969714244, -0.4330127018922193],
                    [0.48296291314453405, 0.12940952255126045, 0.8660254037844386],
                ],
            },
            {
                "type": "orientedPoint",
                "location": {"x": 4.0, "y": 0.5, "z": 1.0},
                "rotation_matrix": [[0, -0.0, -1.0], [0.0, 1.0, -0.0], [1.0, 0.0, 0]],
            },
        ],
    },
    {
        "case": "relion4_star, filter value 3, binning 1, single point",
        "source_cfg": {
            "order": "xyz",
            "file_format": "relion4_star",
            "glob_string": "annotations/relion_4_star.star",
            "shape": "OrientedPoint",
            "is_visualization_default": False,
            "filter_value": "TS_003",
        },
        "count": 1,
        "out_data": [
            {
                "type": "orientedPoint",
                "location": {"x": 1, "y": 0, "z": -1},
                "rotation_matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            },
        ],
    },
    # stopgap_star
    {
        "case": "stopgap_star, filter value 1, binning 4",
        "source_cfg": {
            "order": "xyz",
            "file_format": "stopgap_star",
            "glob_string": "annotations/stopgap_star.star",
            "shape": "OrientedPoint",
            "is_visualization_default": False,
            "filter_value": "1",
            "binning": 4,
        },
        "count": 2,
        "out_data": [
            {
                "type": "orientedPoint",
                "location": {"x": 0.7, "y": 1.4, "z": 2.2},
                "rotation_matrix": [
                    [0.0, 1.0, 0.0],
                    [-0.7071067811865475, -0.0, 0.7071067811865475],
                    [0.7071067811865475, 0.0, 0.7071067811865475],
                ],
            },
            {
                "type": "orientedPoint",
                "location": {"x": 1.8, "y": 1.6, "z": 1.3},
                "rotation_matrix": [
                    [-0.35355339059327356, -0.3535533905932737, 0.8660254037844386],
                    [0.6123724356957947, 0.6123724356957945, 0.4999999999999998],
                    [-0.7071067811865475, 0.7071067811865475, 0.0],
                ],
            },
        ],
    },
    {
        "case": "stopgap_star, filter value 2, binning 2, rotation convention",
        "source_cfg": {
            "order": "xyz",
            "file_format": "stopgap_star",
            "glob_string": "annotations/stopgap_star.star",
            "shape": "OrientedPoint",
            "is_visualization_default": False,
            "filter_value": "2",
            "binning": 2,
        },
        "count": 3,
        "out_data": [
            {
                "type": "orientedPoint",
                "location": {"x": 2.5, "y": 1.0, "z": -0.5},
                "rotation_matrix": [
                    [1.0, 0.0, 0.0],
                    [0.0, 0.0, -1.0],
                    [0.0, 1.0, 0.0],
                ],
            },
            {
                "type": "orientedPoint",
                "location": {"x": 1.5, "y": 4.0, "z": 0.5},
                "rotation_matrix": [
                    [0.6770771969714244, -0.7244443697168013, 0.12940952255126045],
                    [0.5950348471655409, 0.6424020199109172, 0.48296291314453405],
                    [-0.4330127018922193, -0.24999999999999983, 0.8660254037844386],
                ],
            },
            {
                "type": "orientedPoint",
                "location": {"x": 4.0, "y": 3.5, "z": 1.0},
                "rotation_matrix": [
                    [1.0, -0.0, 0.0],
                    [0.0, 0.0, 1.0],
                    [-0.0, -1.0, 0.0],
                ],
            },
        ],
    },
    {
        "case": "stopgap_star, filter value 3, binning 1, single point",
        "source_cfg": {
            "order": "xyz",
            "file_format": "stopgap_star",
            "glob_string": "annotations/stopgap_star.star",
            "shape": "OrientedPoint",
            "is_visualization_default": False,
            "filter_value": "3",
        },
        "count": 1,
        "out_data": [
            {
                "type": "orientedPoint",
                "location": {"x": 5, "y": 4, "z": 3},
                "rotation_matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            },
        ],
    },
]


@pytest.mark.parametrize("case", ingest_oriented_points_test_cases)
def test_ingest_oriented_point_data(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    tomo_importer: TomogramImporter,
    dataset_config: DepositionImportConfig,
    s3_client: S3Client,
    case: Dict[str, Any],
) -> None:

    # loop through test cases
    anno_config = {
        "metadata": default_anno_metadata,
        "sources": [
            case["source_cfg"],
        ],
    }
    dataset_config._set_object_configs("annotation", [anno_config])
    anno = OrientedPointAnnotation(
        config=dataset_config,
        metadata=default_anno_metadata,
        path="test-public-bucket/input_bucket/20002/" + case["source_cfg"]["glob_string"],
        parents={"tomogram": tomo_importer, **tomo_importer.parents},
        identifier=100,
        binning=case["source_cfg"].get("binning"),
        file_format=case["source_cfg"]["file_format"],
        filter_value=case["source_cfg"]["filter_value"],
        order=case["source_cfg"]["order"],
    )
    anno.import_item()
    anno.import_metadata()

    # Strip the bucket name and annotation name from the annotation's output path.
    anno_file = anno.get_output_path() + "_orientedpoint.ndjson"

    # Sanity check the ndjson file
    with s3_fs.open(anno_file, "r") as fh:
        points = ndjson.load(fh)

    # Check length of points
    assert len(points) == case["count"], f"Incorrect number of points for {case['case']}"

    # Check data
    for point, exp_point in zip(points, case["out_data"], strict=True):
        # Type
        assert exp_point["type"] == point["type"], f"Incorrect point type for {case['case']}"

        # Location with specified numerical precision
        loc = point["location"]
        exp_loc = exp_point["location"]
        for dim in ["x", "y", "z"]:
            assert loc[dim] == pytest.approx(
                exp_loc[dim],
                abs=NUMERICAL_PRECISION,
            ), f"Incorrect point data for {case['case']}"

        # Check orientation
        ori = point["rotation_matrix"]
        exp_ori = exp_point["rotation_matrix"]
        for i in range(3):
            assert ori[i] == pytest.approx(
                exp_ori[i],
                abs=NUMERICAL_PRECISION,
            ), f"Incorrect orientation for {case['case']}"


ingest_instance_points_test_cases = [
    # tardis
    {
        "case": "tardis, binning 2",
        "source_cfg": {
            "order": "xyz",
            "file_format": "tardis",
            "glob_string": "annotations/tardis.csv",
            "shape": "InstanceSegmentation",
            "is_visualization_default": False,
            "binning": 2,
        },
        "count": 6,
        "out_data": [
            {
                "type": "instancePoint",
                "location": {"x": 2, "y": 4, "z": 6},
                "instance_id": 0,
            },
            {
                "type": "instancePoint",
                "location": {"x": 2, "y": 2, "z": 2},
                "instance_id": 0,
            },
            {
                "type": "instancePoint",
                "location": {"x": 3, "y": 2, "z": 1},
                "instance_id": 1,
            },
            {
                "type": "instancePoint",
                "location": {"x": 0, "y": 3, "z": 0},
                "instance_id": 1,
            },
            {
                "type": "instancePoint",
                "location": {"x": 4, "y": 2, "z": 1},
                "instance_id": 1,
            },
            {
                "type": "instancePoint",
                "location": {"x": 1.5, "y": 1, "z": 0.5},
                "instance_id": 2,
            },
        ],
    },
]


@pytest.mark.parametrize("case", ingest_instance_points_test_cases)
def test_ingest_instance_point_data(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    tomo_importer: TomogramImporter,
    dataset_config: DepositionImportConfig,
    s3_client: S3Client,
    case: Dict[str, Any],
) -> None:

    # loop through test cases
    anno_config = {
        "metadata": default_anno_metadata,
        "sources": [
            case["source_cfg"],
        ],
    }
    dataset_config._set_object_configs("annotation", [anno_config])

    anno = InstanceSegmentationAnnotation(
        config=dataset_config,
        metadata=default_anno_metadata,
        path="test-public-bucket/input_bucket/20002/" + case["source_cfg"]["glob_string"],
        parents={"tomogram": tomo_importer, **tomo_importer.parents},
        identifier=100,
        binning=case["source_cfg"].get("binning"),
        file_format=anno_config["sources"][0]["file_format"],
    )
    anno.import_item()
    anno.import_metadata()

    # Strip the bucket name and annotation name from the annotation's output path.
    anno_file = anno.get_output_path() + "_instancesegmentation.ndjson"

    # Sanity check the ndjson file
    with s3_fs.open(anno_file, "r") as fh:
        points = ndjson.load(fh)

    # Check length of points
    assert len(points) == case["count"], f"Incorrect number of points for {case['case']}"

    # Check data
    for point, exp_point in zip(points, case["out_data"], strict=True):
        # Type
        assert exp_point["type"] == point["type"], f"Incorrect point type for {case['case']}"

        # Location with specified numerical precision
        loc = point["location"]
        exp_loc = exp_point["location"]
        for dim in ["x", "y", "z"]:
            assert loc[dim] == pytest.approx(
                exp_loc[dim],
                abs=NUMERICAL_PRECISION,
            ), f"Incorrect point data for {case['case']}"

        # Check id
        assert exp_point["instance_id"] == point["instance_id"], f"Incorrect id for {case['case']}"
