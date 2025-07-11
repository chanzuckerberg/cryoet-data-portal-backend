import json
import os.path
from typing import Any, Callable
from unittest.mock import ANY, MagicMock

import cryoet_data_portal_neuroglancer.state_generator as state_generator
import importers
import pytest
from importers.base_importer import BaseImporter
from importers.tomogram import TomogramImporter
from importers.visualization_config import VisualizationConfigImporter
from importers.voxel_spacing import VoxelSpacingImporter
from mypy_boto3_s3 import S3Client

from common.config import DepositionImportConfig
from common.fs import FileSystemApi
from tests.s3_import.util import create_config, get_children, get_data_from_s3, get_run_and_parents


def get_parents(config: DepositionImportConfig) -> dict[str, BaseImporter]:
    parents = get_run_and_parents(config)
    parents["voxel_spacing"] = list(VoxelSpacingImporter.finder(config, **parents))[0]
    parents["tomogram"] = list(TomogramImporter.finder(config, **parents))[0]

    # creates the tomogram volume files required for the visualization config
    parents["tomogram"].import_item()

    return parents


def get_vs_path(parents: dict[str, BaseImporter]) -> str:
    ds_name = parents["dataset"].name
    run_name = parents["run"].name
    vs_name = parents["voxel_spacing"].name
    return f"output/{ds_name}/{run_name}/Reconstructions/VoxelSpacing{vs_name}/"


@pytest.fixture
def expected_config_json() -> dict[str, str]:
    return {"key": "combine_json_layers", "foo": "bar"}


@pytest.fixture
def expected_tomogram_layer() -> dict[str, str]:
    return {"key": "generate_image_layer", "random": "value"}


@pytest.fixture
def expected_url() -> str:
    return "https://test.domain.com"


@pytest.fixture
def config(s3_fs: FileSystemApi, test_output_bucket: str, expected_url: str) -> DepositionImportConfig:
    config = create_config(s3_fs, test_output_bucket)
    config.write_zarr = True
    config.https_prefix = expected_url
    return config


@pytest.fixture
def validate_config(
    s3_client: S3Client,
    test_output_bucket: str,
    mock_state_generator: MagicMock,
    expected_url: str,
    expected_tomogram_layer: dict[str, str],
    expected_config_json: dict[str, str],
) -> Callable[[str, dict[str, BaseImporter], list[dict]], None]:
    def validate(vs_path: str, parents: dict[str, BaseImporter], anno_layers: list[dict] = None) -> None:
        key = os.path.join(vs_path, "NeuroglancerPrecompute", "100-neuroglancer_config.json")
        actual = json.loads(get_data_from_s3(s3_client, test_output_bucket, key).read())
        for key, val in expected_config_json.items():
            assert actual[key] == val, f"Key {key} does not match"

        layers = [expected_tomogram_layer] + (anno_layers or [])
        scale = (parents["voxel_spacing"].as_float() * 1e-10,) * 3
        tomo_volume_info = parents["tomogram"].get_output_volume_info()
        contrast_limits = parents["tomogram"].get_tomogram().get_contrast_limits()
        mock_state_generator.generate_image_layer.assert_called_once_with(
            os.path.relpath(os.path.join(vs_path, "Tomograms", "100", "TS_run1.zarr"), "output"),
            scale=scale,
            url=expected_url,
            name=parents["run"].name,
            start={"x": 0, "y": 0, "z": 0},
            size=tomo_volume_info.get_dimensions(),
            mean=tomo_volume_info.dmean,
            rms=tomo_volume_info.rms,
            threedee_contrast_limits=contrast_limits,
        )
        mock_state_generator.combine_json_layers.assert_called_once_with(layers, scale=scale)

    return validate


@pytest.fixture
def mock_state_generator(
    monkeypatch: pytest.MonkeyPatch,
    expected_tomogram_layer: dict[str, str],
    expected_config_json: dict[str, str],
) -> MagicMock:
    state_generator_mock = MagicMock(spec=state_generator)
    monkeypatch.setattr(importers.visualization_config, "state_generator", state_generator_mock)
    state_generator_mock.generate_image_layer.return_value = expected_tomogram_layer
    state_generator_mock.combine_json_layers.return_value = expected_config_json
    yield state_generator_mock


def test_viz_config_with_only_tomogram(
    test_output_bucket: str,
    s3_client: S3Client,
    config: DepositionImportConfig,
    validate_config: Callable[[str, dict[str, BaseImporter], list[dict]], None],
) -> None:
    parents = get_parents(config)

    viz_config = list(VisualizationConfigImporter.finder(config, **parents))
    for item in viz_config:
        item.import_item()

    vs_path = get_vs_path(parents)
    prefix = os.path.join(vs_path, "NeuroglancerPrecompute")
    config_files = get_children(s3_client, test_output_bucket, prefix)
    expected_file_name = "100-neuroglancer_config.json"
    assert expected_file_name in config_files
    validate_config(vs_path, parents)


def test_no_viz_config_for_is_visualization_default_false(
    test_output_bucket: str,
    s3_client: S3Client,
    config: DepositionImportConfig,
) -> None:
    parents = get_parents(config)

    parents["tomogram"].metadata["is_visualization_default"] = False

    viz_config = list(VisualizationConfigImporter.finder(config, **parents))
    for item in viz_config:
        item.import_item()

    prefix = os.path.join(get_vs_path(parents), "NeuroglancerPrecompute")
    config_files = get_children(s3_client, test_output_bucket, prefix)
    assert set() == config_files


@pytest.fixture(
    params=[
        ("Point", "ndjson"),
        ("OrientedPoint", "ndjson"),
        ("OrientedPointMesh", "ndjson"),
        ("InstanceSegmentation", "ndjson"),
        ("SegmentationMask", "zarr"),
        ("SegmentationMask", "mrc"),
        ("Mesh", "glb"),
    ],
)
def shape_and_format(request) -> tuple[str, str]:
    return request.param


@pytest.fixture(params=[True, False])
def is_visualization_default(request) -> bool:
    return request.param


@pytest.fixture
def annotation_usecases(
    shape_and_format: tuple[str, str], is_visualization_default: bool, expected_url: str,
) -> dict[str, Any]:
    shape, format = shape_and_format
    has_mesh = False
    if shape == "OrientedPointMesh":
        has_mesh = True
        shape = "OrientedPoint"
    annotation_files = {
        "shape": shape,
        "format": format,
        "is_visualization_default": is_visualization_default,
    }
    generator_method = None
    input_args = {
        "name": "100 FAS ",
        "url": expected_url,
        "color": ANY,
        "is_visible": is_visualization_default,
    }
    return_value = None
    if format == "ndjson":
        if shape in {"Point", "InstanceSegmentation"}:
            generator_method = "generate_point_layer"
            input_args["name"] += "point"
        elif shape == "OrientedPoint":
            generator_method = "generate_oriented_point_layer"
            input_args["name"] += "orientedpoint"
        input_args["is_instance_segmentation"] = shape == "InstanceSegmentation"

        return_value = {"key": generator_method, "random": "value"}
    elif shape == "SegmentationMask" and format == "zarr":
        generator_method = "generate_segmentation_mask_layer"
        input_args["name"] += "segmentation"
        return_value = {"key": generator_method, "random": "value"}

    args = {
        "shape": shape,
        "annotation_files": [annotation_files],
        "generator_method": generator_method,
        "generator_args": input_args,
        "generator_return_value": return_value,
    }
    if has_mesh:
        args["mesh_source_path"] = "output/dummy_mesh.glb"
    return args


def put_annotation_metadata_file(
    s3_client: S3Client,
    test_output_bucket: str,
    annotation_usecases: dict[str, Any],
    parents: dict[str, BaseImporter],
):
    annotation_metadata = {
        "annotation_method": "CNN predictions",
        "annotation_object": {"name": "FAS", "id": "GO:0005835"},
        "deposition_id": 10301,
        "ground_truth_status": True,
        "alignment_metadata_path": f"{parents['dataset'].name}/TS_run1/Alignments/100/alignment_metadata.json",
        "files": annotation_usecases["annotation_files"],
    }
    annotation_metadata_path = os.path.join(
        get_vs_path(parents), "Annotations", "100", "fatty_acid_synthase_complex-1.0.json",
    )
    if annotation_usecases.get("mesh_source_path"):
        annotation_mesh_path = os.path.join(
            get_vs_path(parents),
            "NeuroglancerPrecompute",
            "100-fatty_acid_synthase_complex-1.0_orientedmesh",
        )
        s3_client.put_object(
            Bucket=test_output_bucket,
            Key=annotation_mesh_path,
            Body=b"",
        )
    s3_client.put_object(Bucket=test_output_bucket, Key=annotation_metadata_path, Body=json.dumps(annotation_metadata))


def test_viz_config_with_tomogram_and_annotation(
    test_output_bucket: str,
    s3_client: S3Client,
    config: DepositionImportConfig,
    validate_config: Callable[[str, dict[str, BaseImporter], list[dict]], None],
    mock_state_generator: MagicMock,
    annotation_usecases: dict[str, Any],
) -> None:
    parents = get_parents(config)
    # Creates annotation metadata file
    put_annotation_metadata_file(s3_client, test_output_bucket, annotation_usecases, parents)

    vs_path = get_vs_path(parents)
    anno_layers = []
    if method := annotation_usecases["generator_method"]:
        mock_state_generator.__getattr__(method).return_value = annotation_usecases["generator_return_value"]
        anno_layers.append(annotation_usecases["generator_return_value"])

    # Oriented point mesh layers are currently a little special as they
    # generate two output layers for one single input shape + annotation combo
    # as opposed to the other annotation shapes which only generate one layer.
    # Instead of fully refactoring the test code to handle this right now
    # across all annotation types we check for this special case
    # and then do some extra steps and adjustments
    oriented_point_mesh = False
    if annotation_usecases["shape"] == "OrientedPoint" and annotation_usecases.get("mesh_source_path"):
        oriented_point_mesh = True
        mock_state_generator.generate_oriented_point_mesh_layer.return_value = {
            "key": "generate_oriented_point_mesh_layer",
            "random": "value",
        }
        anno_layers.append(mock_state_generator.generate_oriented_point_mesh_layer.return_value)
        anno_layers[0], anno_layers[1] = anno_layers[1], anno_layers[0]  # Ensure mesh layer is first

    viz_config = list(VisualizationConfigImporter.finder(config, **parents))
    for item in viz_config:
        item.import_item()

    prefix = os.path.join(vs_path, "NeuroglancerPrecompute")
    assert "100-neuroglancer_config.json" in get_children(s3_client, test_output_bucket, prefix)
    validate_config(vs_path, parents, anno_layers)

    # If a layer can be generated for an annotation, we should have called the method with the correct args
    if method_name := annotation_usecases["generator_method"]:
        shape = annotation_usecases["shape"].lower()
        precompute_path = f"{vs_path}/NeuroglancerPrecompute/100-fatty_acid_synthase_complex-1.0_{shape}"
        args = {
            **annotation_usecases["generator_args"],
            "source": os.path.relpath(precompute_path, "output"),
            "scale": (parents["voxel_spacing"].as_float() * 1e-10,) * 3,
        }
        if oriented_point_mesh:
            args["is_visible"] = False

        mock_state_generator.__getattr__(method_name).assert_called_once_with(**args)

    if oriented_point_mesh:
        shape = "orientedmesh"
        precompute_path = f"{vs_path}/NeuroglancerPrecompute/100-fatty_acid_synthase_complex-1.0_{shape}"
        args = {
            **annotation_usecases["generator_args"],
            "source": os.path.relpath(precompute_path, "output"),
            "scale": (parents["voxel_spacing"].as_float() * 1e-10,) * 3,
        }
        args["name"] = args["name"].replace("orientedpoint", shape)
        args.pop("is_instance_segmentation", None)
        mock_state_generator.generate_oriented_point_mesh_layer.assert_called_once_with(**args)
