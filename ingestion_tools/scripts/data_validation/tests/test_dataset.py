from typing import Dict

import allure
import pytest
from tests.helper_images import check_photo_valid
from tests.helper_metadata import basic_metadata_check
from tests.test_deposition import HelperTestDeposition

from common.fs import FileSystemApi


@pytest.mark.dataset
class TestDataset:
    @allure.title("Sanity check dataset metadata.")
    def test_dataset_metadata(self, dataset_metadata: Dict):
        assert dataset_metadata["dataset_description"]
        assert dataset_metadata["dataset_title"]
        assert dataset_metadata["dataset_identifier"]
        basic_metadata_check(dataset_metadata)

    @allure.title("Valid key photos (if they exist).")
    def test_dataset_key_photos(self, dataset_metadata: Dict, bucket: str, filesystem: FileSystemApi):
        if thumbnail := dataset_metadata["key_photos"]["thumbnail"]:
            check_photo_valid(thumbnail, bucket, filesystem)

        if snapshot := dataset_metadata["key_photos"]["snapshot"]:
            check_photo_valid(snapshot, bucket, filesystem)

    @allure.title("Valid corresponding deposition metadata.")
    def test_dataset_deposition(self, dataset_metadata: Dict, bucket: str, filesystem: FileSystemApi):
        HelperTestDeposition.check_deposition_metadata(dataset_metadata["deposition_id"], bucket, filesystem)
