import os
import sys
from typing import Dict

import pytest

from common.fs import FileSystemApi

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from test_deposition import TestDeposition


@pytest.mark.annotation
@pytest.mark.metadata
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestAnnotationMetadata:
    def test_annotation_metadata(
        self,
        annotation_metadata: Dict[str, Dict],
        bucket: str,
        filesystem: FileSystemApi,
    ):
        """Sanity check for annotation metadata and corresponding deposition metadata."""
        for metadata in annotation_metadata.values():
            assert metadata["deposition_id"]
            assert isinstance(metadata["annotation_object"], dict)
            assert isinstance(metadata["authors"], list)
            assert isinstance(metadata["authors"][0], dict)
            assert metadata["object_count"] >= 0
            assert len(metadata["files"]) >= 0
            TestDeposition.check_deposition_metadata(metadata["deposition_id"], bucket, filesystem)
