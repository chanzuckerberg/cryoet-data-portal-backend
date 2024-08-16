from typing import Dict

import pytest
from tests.test_deposition import HelperTestDeposition

from common.fs import FileSystemApi


@pytest.mark.annotation
@pytest.mark.metadata
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestAnnotationMetadata:
    def test_annotation_metadata(
        self,
        annotation_metadata: Dict[str, Dict],
    ):
        """Sanity check for annotation metadata and corresponding deposition metadata."""
        for metadata in annotation_metadata.values():
            assert metadata["deposition_id"]
            assert isinstance(metadata["annotation_object"], dict)
            assert isinstance(metadata["authors"], list)
            assert isinstance(metadata["authors"][0], dict)
            assert metadata["object_count"] >= 0
            assert len(metadata["files"]) >= 0

    def test_annotation_deposition(
        self,
        annotation_metadata: Dict[str, Dict],
        bucket: str,
        filesystem: FileSystemApi,
    ):
        """Check that the deposition metadata is correct."""
        for metadata in annotation_metadata.values():
            HelperTestDeposition.check_deposition_metadata(metadata["deposition_id"], bucket, filesystem)
