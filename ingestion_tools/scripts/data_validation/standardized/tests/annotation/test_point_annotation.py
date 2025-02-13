from typing import Dict, List

import allure
import pytest
from data_validation.standardized.tests.annotation.helper_point import contained_in_tomo, point_count_consistent


@pytest.mark.annotation
@pytest.mark.parametrize("dataset, run_name, voxel_spacing", pytest.cryoet.dataset_run_spacing_combinations, scope="session")
class TestPointAnnotations:
    ### BEGIN Self-consistency tests ###
    @allure.title("Point: number of annotations is consistent between metadata and ndjson file.")
    def test_point_count_consistent(
        self,
        point_annotations: Dict[str, List[Dict]],
        annotation_metadata: Dict[str, Dict],
        point_annotation_files_to_metadata_files: Dict[str, str],
    ):
        point_count_consistent(point_annotations, annotation_metadata, point_annotation_files_to_metadata_files)

    ### END Self-consistency tests ###

    ### BEGIN Tomogram-consistency tests ###
    @allure.title("Point: annotations are contained within the tomogram dimensions.")
    def test_contained_in_tomo(
        self,
        point_annotations: Dict[str, List[Dict]],
        point_annotation_files_to_metadata: Dict[str, str],
        all_vs_tomogram_metadata: Dict,
    ):
        contained_in_tomo(point_annotations, point_annotation_files_to_metadata, all_vs_tomogram_metadata)

    ### END Tomogram-consistency tests ###
