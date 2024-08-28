from typing import Dict

import pytest
from tests.helper_metadata import basic_metadata_check
from tests.test_deposition import HelperTestDeposition

from common.fs import FileSystemApi


@pytest.mark.annotation
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestAnnotationMetadata:
    """A class dedicated to the general testing of all annotation metadata."""

    def test_annotation_metadata(
        self,
        annotation_metadata: Dict[str, Dict],
    ):
        """Sanity check for annotation metadata and corresponding deposition metadata."""
        for metadata in annotation_metadata.values():
            assert isinstance(metadata["annotation_object"], dict)
            assert isinstance(metadata["annotation_object"]["name"], str)
            assert isinstance(metadata["annotation_object"]["id"], str)
            assert metadata["object_count"] >= 0
            assert len(metadata["files"]) >= 0
            basic_metadata_check(metadata)

    def test_annotation_deposition(
        self,
        annotation_metadata: Dict[str, Dict],
        bucket: str,
        filesystem: FileSystemApi,
    ):
        """Check that the deposition metadata is correct."""
        for metadata in annotation_metadata.values():
            HelperTestDeposition.check_deposition_metadata(metadata["deposition_id"], bucket, filesystem)
