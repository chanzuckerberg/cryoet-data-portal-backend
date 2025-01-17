from typing import Dict

import allure
import pytest
from data_validation.tests.helper_metadata import basic_metadata_check
from data_validation.tests.test_deposition import HelperTestDeposition

from common.fs import FileSystemApi


@pytest.mark.annotation
@pytest.mark.parametrize("dataset, run_name, voxel_spacing", pytest.cryoet.dataset_run_spacing_combinations, scope="session")
class TestAnnotationMetadata:
    """A class dedicated to the general testing of all annotation metadata."""

    @allure.title("Annotation metadata: sanity check annotation metadata.")
    def test_metadata(
        self,
        annotation_metadata: Dict[str, Dict],
    ):
        for metadata in annotation_metadata.values():
            assert isinstance(metadata["annotation_object"], dict)
            assert isinstance(metadata["annotation_object"]["name"], str)
            assert isinstance(metadata["annotation_object"]["id"], str)
            assert metadata["object_count"] >= 0
            assert len(metadata["files"]) >= 0
            basic_metadata_check(metadata)

    @allure.title("Annotation metadata: valid corresponding deposition metadata.")
    def test_deposition_id(
        self,
        annotation_metadata: Dict[str, Dict],
        bucket: str,
        filesystem: FileSystemApi,
    ):
        for metadata in annotation_metadata.values():
            HelperTestDeposition.check_deposition_metadata(metadata["deposition_id"], bucket, filesystem)
