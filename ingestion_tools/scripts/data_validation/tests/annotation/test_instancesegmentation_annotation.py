from typing import Dict, List

import allure
import pytest
from data_validation.tests.annotation.helper_point import contained_in_tomo


@pytest.mark.annotation
@pytest.mark.parametrize("dataset, run_name, voxel_spacing", pytest.dataset_run_spacing_combinations, scope="session")
class TestInstanceSegmentationAnnotations:
    ### BEGIN Self-consistency tests ###

    @allure.title("Instance segmentation: number of unique annotations is consistent between metadata and ndjson file.")
    def test_instance_count_consistent(
        self,
        instance_seg_annotations: Dict[str, List[Dict]],
        annotation_metadata: Dict[str, Dict],
        instance_seg_annotation_files_to_metadata_files: Dict[str, str],
    ):
        unique_instance_ids = set()
        for filename, points in instance_seg_annotations.items():
            print(f"\tFile: {filename}")
            metadata_file = instance_seg_annotation_files_to_metadata_files[filename]
            metadata = annotation_metadata[metadata_file]
            for ann in points:
                unique_instance_ids.add(ann["instance_id"])
            assert len(unique_instance_ids) == metadata["object_count"]

    ### END Self-consistency tests ###

    ### BEGIN Tomogram-consistency tests ###
    @allure.title("Instance segmentation: annotations are contained within the tomogram dimensions.")
    def test_contained_in_tomo(
        self,
        instance_seg_annotations: Dict[str, List[Dict]],
        instance_seg_annotation_files_to_metadata: Dict[str, str],
        all_vs_tomogram_metadata: Dict,
    ):
        contained_in_tomo(instance_seg_annotations, instance_seg_annotation_files_to_metadata, all_vs_tomogram_metadata)

    ### END Tomogram-consistency tests ###
