from typing import Dict

import pytest
from data_validation.tests.helper_images import check_photo_valid
from data_validation.tests.helper_metadata import basic_metadata_check
from data_validation.tests.test_deposition import HelperTestDeposition

from common.fs import FileSystemApi


@pytest.mark.dataset
class TestDataset:
    def test_dataset_metadata(self, dataset_metadata: Dict):
        """A dataset metadata sanity check."""
        assert dataset_metadata["dataset_description"]
        assert dataset_metadata["dataset_title"]
        assert dataset_metadata["dataset_identifier"]
        basic_metadata_check(dataset_metadata)

    def test_dataset_key_photos(self, dataset_metadata: Dict, bucket: str, filesystem: FileSystemApi):
        """Check that the key_photos in the metadata are valid."""
        if thumbnail := dataset_metadata["key_photos"]["thumbnail"]:
            check_photo_valid(thumbnail, bucket, filesystem)

        if snapshot := dataset_metadata["key_photos"]["snapshot"]:
            check_photo_valid(snapshot, bucket, filesystem)

    def test_dataset_deposition(self, dataset_metadata: Dict, bucket: str, filesystem: FileSystemApi):
        HelperTestDeposition.check_deposition_metadata(dataset_metadata["deposition_id"], bucket, filesystem)
