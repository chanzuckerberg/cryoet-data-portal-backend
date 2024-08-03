import datetime
from typing import Any, Callable

import pytest as pytest
from tests.db_import.populate_db import (
    ANNOTATION_AUTHOR_ID,
    ANNOTATION_FILE_ID,
    ANNOTATION_ID,
    DATASET_ID,
    TOMOGRAM_VOXEL_ID1,
    populate_annotation_authors,
    populate_annotation_files,
    populate_stale_annotation_authors,
    populate_stale_annotation_files,
)

import common.db_models as models


@pytest.fixture
def expected_annotations(http_prefix: str) -> list[dict[str, Any]]:
    path = f"{DATASET_ID}/RUN1/Tomograms/VoxelSpacing12.300/Annotations/100-foo-1.0.json"
    return [
        {
            "id": ANNOTATION_ID,
            "tomogram_voxel_spacing_id": TOMOGRAM_VOXEL_ID1,
            "s3_metadata_path": f"s3://test-public-bucket/{path}",
            "https_metadata_path": f"{http_prefix}/{path}",
            "deposition_date": datetime.date(2023, 4, 1),
            "release_date": datetime.date(2023, 6, 1),
            "last_modified_date": datetime.date(2023, 6, 1),
            "annotation_publication": "EMPIAR-XYZ",
            "annotation_method": "2D CNN predictions",
            "ground_truth_status": True,
            "object_name": "foo",
            "object_id": "GO:000000",
            "annotation_software": "pyTOM + Keras",
            "is_curator_recommended": True,
            "object_count": 16,
            "deposition_id": 111111,
            "method_type": "hybrid",
            "method_links": [
                {
                    "link": "https://fake-link.com/resources/100-foo-1.0_method.pdf",
                    "link_type": "documentation",
                    "name": "Method Documentation",
                },
                {
                    "link": "https://another-link.com/100-foo-1.0_code.zip",
                    "link_type": "source_code",
                    "name": "Source Code",
                },
            ],
        },
    ]


@pytest.fixture
def expected_annotation_files(http_prefix: str) -> list[dict[str, Any]]:
    path = f"{DATASET_ID}/RUN1/Tomograms/VoxelSpacing12.300/Annotations/"
    return [
        {
            "id": ANNOTATION_FILE_ID,
            "annotation_id": ANNOTATION_ID,
            "s3_path": f"s3://test-public-bucket/{path}100-foo-1.0_point.ndjson",
            "https_path": f"{http_prefix}/{path}100-foo-1.0_point.ndjson",
            "shape_type": "Point",
            "format": "ndjson",
            "is_visualization_default": True,
        },
        {
            "annotation_id": ANNOTATION_ID,
            "s3_path": f"s3://test-public-bucket/{path}100-foo-1.0_segmask.mrc",
            "https_path": f"{http_prefix}/{path}100-foo-1.0_segmask.mrc",
            "shape_type": "SegmentationMask",
            "format": "mrc",
            "is_visualization_default": False,
        },
        {
            "annotation_id": ANNOTATION_ID,
            "s3_path": f"s3://test-public-bucket/{path}100-foo-1.0_segmask.zarr",
            "https_path": f"{http_prefix}/{path}100-foo-1.0_segmask.zarr",
            "shape_type": "SegmentationMask",
            "format": "zarr",
            "is_visualization_default": False,
        },
    ]


@pytest.fixture
def expected_annotation_authors() -> list[dict[str, Any]]:
    return [
        {
            "id": ANNOTATION_AUTHOR_ID,
            "annotation_id": ANNOTATION_ID,
            "name": "Jane Smith",
            "corresponding_author_status": False,
            "primary_annotator_status": True,
            "primary_author_status": True,
            "author_list_order": 1,
        },
        {
            "annotation_id": ANNOTATION_ID,
            "name": "J Carpenter",
            "corresponding_author_status": False,
            "primary_annotator_status": True,
            "primary_author_status": True,
            "author_list_order": 2,
        },
        {
            "annotation_id": ANNOTATION_ID,
            "name": "John Doe",
            "corresponding_author_status": False,
            "primary_annotator_status": False,
            "primary_author_status": False,
            "orcid": "0000-0000-1234-0000",
            "email": "jdoe@test.com",
            "author_list_order": 3,
        },
    ]


# Tests addition and update  of annotations and annotation files
def test_import_annotations(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    expected_annotations: list[dict[str, Any]],
    expected_annotation_files: list[dict[str, Any]],
) -> None:
    populate_annotation_files()
    verify_dataset_import(["--import-annotations"])
    expected_annotations_iter = iter(expected_annotations)
    expected_annotations_files_iter = iter(expected_annotation_files)
    actual_voxel_spacing = models.TomogramVoxelSpacing.get(id=TOMOGRAM_VOXEL_ID1)
    for annotation in actual_voxel_spacing.annotations.order_by(models.Annotation.s3_metadata_path):
        verify_model(annotation, next(expected_annotations_iter))
        assert len(annotation.files) == len(expected_annotation_files)
        for file in annotation.files.order_by(models.AnnotationFiles.shape_type, models.AnnotationFiles.format):
            verify_model(file, next(expected_annotations_files_iter))
        assert len(annotation.authors) == 0


# Tests state annotation and files are removed
def test_import_annotations_files_removes_stale(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    expected_annotations: list[dict[str, Any]],
    expected_annotation_files: list[dict[str, Any]],
) -> None:
    populate_annotation_files()
    populate_stale_annotation_files()
    verify_dataset_import(["--import-annotations"])
    expected_annotations_iter = iter(expected_annotations)
    expected_annotations_files_iter = iter(expected_annotation_files)
    actual_voxel_spacing = models.TomogramVoxelSpacing.get(id=TOMOGRAM_VOXEL_ID1)
    for annotation in actual_voxel_spacing.annotations.order_by(models.Annotation.s3_metadata_path):
        verify_model(annotation, next(expected_annotations_iter))
        assert len(annotation.files) == len(expected_annotation_files)
        for file in annotation.files.order_by(models.AnnotationFiles.shape_type, models.AnnotationFiles.format):
            verify_model(file, next(expected_annotations_files_iter))
        assert len(annotation.authors) == 0


# Tests update of existing annotation authors, addition of new authors
def test_import_annotation_authors(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    expected_annotations: list[dict[str, Any]],
    expected_annotation_authors: list[dict[str, Any]],
) -> None:
    populate_annotation_authors()
    verify_dataset_import(["--import-annotation-authors"])
    expected_annotations_authors_iter = iter(expected_annotation_authors)
    actual_voxel_spacing = models.TomogramVoxelSpacing.get(id=TOMOGRAM_VOXEL_ID1)
    for annotation in actual_voxel_spacing.annotations.order_by(models.Annotation.s3_metadata_path):
        assert len(annotation.authors) == len(expected_annotation_authors)
        for author in annotation.authors.order_by(models.AnnotationAuthor.author_list_order):
            verify_model(author, next(expected_annotations_authors_iter))


# Tests deletion of stale annotation and annotation authors
def test_import_annotation_authors_removes_stale(
    verify_dataset_import: Callable[[list[str]], models.Dataset],
    verify_model: Callable[[models.BaseModel, dict[str, Any]], None],
    expected_annotations: list[dict[str, Any]],
    expected_annotation_authors: list[dict[str, Any]],
) -> None:
    populate_annotation_authors()
    populate_stale_annotation_authors()
    verify_dataset_import(["--import-annotation-authors"])
    expected_annotations_authors_iter = iter(expected_annotation_authors)
    actual_voxel_spacing = models.TomogramVoxelSpacing.get(id=TOMOGRAM_VOXEL_ID1)
    for annotation in actual_voxel_spacing.annotations.order_by(models.Annotation.s3_metadata_path):
        assert len(annotation.authors) == len(expected_annotation_authors)
        for author in annotation.authors.order_by(models.AnnotationAuthor.author_list_order):
            verify_model(author, next(expected_annotations_authors_iter))
