"""
key_images testing is also done here (since key_images are part of the tomogram metadata)
"""

from typing import Dict

import pytest
from helpers_images import check_photo_valid
from test_deposition import TestDeposition

from common.fs import FileSystemApi


@pytest.mark.tomogram
@pytest.mark.metadata
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestTomogram:
    def test_tomogram_metadata(self, canonical_tomogram_metadata: Dict):
        """A tomogram metadata sanity check."""
        assert canonical_tomogram_metadata["deposition_id"]
        assert isinstance(canonical_tomogram_metadata["authors"], list)
        assert isinstance(canonical_tomogram_metadata["authors"][0], dict)

    # The key_photo attribute is where the key_images data is stored and can be validated
    def test_tomogram_key_photos(self, canonical_tomogram_metadata: Dict, bucket: str, filesystem: FileSystemApi):
        """Check that the key_photos in the metadata are valid."""
        if (thumbnail := canonical_tomogram_metadata["key_photo"]["thumbnail"]) is not None:
            check_photo_valid(thumbnail, bucket, filesystem)

        if (snapshot := canonical_tomogram_metadata["key_photo"]["snapshot"]) is not None:
            check_photo_valid(snapshot, bucket, filesystem)

    def test_tomogram_deposition(self, canonical_tomogram_metadata: Dict, bucket: str, filesystem: FileSystemApi):
        TestDeposition.check_deposition_metadata(canonical_tomogram_metadata["deposition_id"], bucket, filesystem)
