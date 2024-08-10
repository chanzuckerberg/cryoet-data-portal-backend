from typing import Dict

import pytest
from helpers_images import check_photo_valid
from test_deposition import TestDeposition

from common.fs import FileSystemApi


@pytest.mark.dataset
@pytest.mark.metadata
class TestDataset:
    def test_dataset_metadata(self, dataset_metadata: Dict):
        """A dataset metadata sanity check."""
        assert dataset_metadata["dataset_description"]
        assert dataset_metadata["dataset_title"]
        assert dataset_metadata["dataset_identifier"]
        assert dataset_metadata["deposition_id"]
        assert isinstance(dataset_metadata["authors"], list)
        assert isinstance(dataset_metadata["authors"][0], dict)

    def test_dataset_key_photos(self, dataset_metadata: Dict, bucket: str, filesystem: FileSystemApi):
        """Check that the key_photos in the metadata are valid."""
        if (thumbnail := dataset_metadata["key_photos"]["thumbnail"]) is not None:
            check_photo_valid(thumbnail, bucket, filesystem)

        if (snapshot := dataset_metadata["key_photos"]["snapshot"]) is not None:
            check_photo_valid(snapshot, bucket, filesystem)

    def test_dataset_deposition(self, dataset_metadata: Dict, bucket: str, filesystem: FileSystemApi):
        TestDeposition.check_deposition_metadata(dataset_metadata["deposition_id"], bucket, filesystem)
