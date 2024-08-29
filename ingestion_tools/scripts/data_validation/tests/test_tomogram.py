"""
key_images testing is also done here (since key_images are part of the tomogram metadata)
"""

from typing import Dict

import pytest
from tests.helper_images import check_photo_valid
from tests.test_deposition import HelperTestDeposition

from common.fs import FileSystemApi

# values are based on ingestion_tools/scripts/importers/key_image.py (134 pixels is the min width)
# and frontend aspect ratio (4:3 is used for image display)
PHOTO_ASPECT_RATIO = 4 / 3
MIN_THUMBNAIL_WIDTH = 134
MIN_SNAPSHOT_WIDTH = 512 * 3 / 4  # account for 4:3 aspect ratio


@pytest.mark.tomogram
@pytest.mark.metadata
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestTomogram:
    def test_tomogram_metadata(self, canonical_tomogram_metadata: Dict):
        """A tomogram metadata sanity check."""
        assert canonical_tomogram_metadata["deposition_id"]
        assert isinstance(canonical_tomogram_metadata["authors"], list)
        assert all(isinstance(authors, dict) for authors in canonical_tomogram_metadata["authors"])

    # The key_photo attribute is where the key_images data is stored and can be validated
    def test_tomogram_key_photos(self, canonical_tomogram_metadata: Dict, bucket: str, filesystem: FileSystemApi):
        """Check that the key_photos in the metadata are valid."""
        check_photo_valid(
            canonical_tomogram_metadata["key_photo"]["thumbnail"],
            bucket,
            filesystem,
            MIN_THUMBNAIL_WIDTH,
            PHOTO_ASPECT_RATIO,
        )
        check_photo_valid(
            canonical_tomogram_metadata["key_photo"]["snapshot"],
            bucket,
            filesystem,
            MIN_SNAPSHOT_WIDTH,
            PHOTO_ASPECT_RATIO,
        )

    def test_tomogram_deposition(self, canonical_tomogram_metadata: Dict, bucket: str, filesystem: FileSystemApi):
        HelperTestDeposition.check_deposition_metadata(canonical_tomogram_metadata["deposition_id"], bucket, filesystem)
