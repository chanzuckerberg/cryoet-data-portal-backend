import os

import pytest
from importers.annotation import TriangularMeshAnnotation
from importers.visualization_precompute import (
    AnnotationVisualizationImporter,
    get_annotation_neuroglancer_precompute_path,
)
from importers.voxel_spacing import VoxelSpacingImporter
from mypy_boto3_s3 import S3Client

from common.config import DepositionImportConfig
from common.fs import FileSystemApi
from tests.s3_import.util import create_config, get_run_and_parents, list_dir

mesh_anno_metadata = {
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
    "ground_truth_status": True,
    "authors": [{"name": "Author 1", "ORCID": "0000-0000-0000-0000", "primary_author_status": True}],
    "version": "1.0",
    "is_curator_recommended": True,
}


@pytest.fixture
def config(s3_fs: FileSystemApi, test_output_bucket: str) -> DepositionImportConfig:
    return create_config(s3_fs, test_output_bucket)


@pytest.fixture
def mesh_fixture_path(local_test_data_dir: str) -> str:
    return os.path.join(local_test_data_dir, "fixtures", "annotations", "triangular_mesh.glb")


@pytest.fixture
def mesh_annotation(
    config: DepositionImportConfig,
    s3_client: S3Client,
    test_output_bucket: str,
    mesh_fixture_path: str,
) -> TriangularMeshAnnotation:
    parents = get_run_and_parents(config)
    parents["voxel_spacing"] = list(VoxelSpacingImporter.finder(config, **parents))[0]
    annotation = TriangularMeshAnnotation(
        config=config,
        metadata=mesh_anno_metadata,
        path=mesh_fixture_path,
        parents=parents,
        file_format="glb",
        identifier=100,
        alignment_metadata_path="foo",
    )
    # Put the converted glb in its output location, as the annotation import would have done.
    glb_path = annotation.get_output_filename(annotation.get_output_path(), "glb")
    s3_client.upload_file(mesh_fixture_path, test_output_bucket, glb_path.split("/", 1)[1])
    return annotation


def test_mesh_annotation_precompute(
    config: DepositionImportConfig,
    mesh_annotation: TriangularMeshAnnotation,
    s3_client: S3Client,
    test_output_bucket: str,
) -> None:
    """The glb of a mesh annotation lives in s3, but trimesh can only read local files."""
    viz = AnnotationVisualizationImporter(
        config=config,
        metadata={},
        name="neuroglancer",
        path=None,
        parents={"annotation": mesh_annotation, **mesh_annotation.parents},
    )

    viz.import_item()

    precompute_path = get_annotation_neuroglancer_precompute_path(
        mesh_annotation.get_output_path(),
        viz.get_output_path(),
        "TriangularMesh",
    )
    prefix = precompute_path.split("/", 1)[1]
    files = {os.path.relpath(item, prefix) for item in list_dir(s3_client, test_output_bucket, prefix)}
    assert "info" in files
    assert "segment_properties/info" in files
    assert any(item.startswith("mesh/") for item in files)
