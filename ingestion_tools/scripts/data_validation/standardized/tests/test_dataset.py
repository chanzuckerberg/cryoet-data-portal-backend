from typing import Dict

import allure
import pytest

from common.fs import FileSystemApi
from data_validation.standardized.tests.helper_images import check_photo_valid
from data_validation.standardized.tests.helper_metadata import basic_metadata_check
from data_validation.standardized.tests.test_deposition import HelperTestDeposition


@pytest.mark.dataset
@pytest.mark.parametrize("dataset", pytest.cryoet.dataset, scope="session")
class TestDataset:
    @allure.title("Dataset: sanity check dataset metadata.")
    def test_metadata(self, dataset_metadata: Dict):
        assert dataset_metadata["dataset_description"]
        assert dataset_metadata["dataset_title"]
        assert dataset_metadata["dataset_identifier"]
        basic_metadata_check(dataset_metadata)

    @allure.title("Dataset: valid key photos (if they exist).")
    def test_key_photos(self, dataset_metadata: Dict, bucket: str, filesystem: FileSystemApi):
        if thumbnail := dataset_metadata["key_photos"]["thumbnail"]:
            check_photo_valid(thumbnail, bucket, filesystem)

        if snapshot := dataset_metadata["key_photos"]["snapshot"]:
            check_photo_valid(snapshot, bucket, filesystem)

    @allure.title("Dataset: valid corresponding deposition metadata.")
    def test_deposition_id(self, dataset_metadata: Dict, bucket: str, filesystem: FileSystemApi):
        HelperTestDeposition.check_deposition_metadata(dataset_metadata["deposition_id"], bucket, filesystem)
