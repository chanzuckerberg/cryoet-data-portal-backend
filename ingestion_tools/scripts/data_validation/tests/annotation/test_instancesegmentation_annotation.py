from typing import Dict, List

import pytest
from data_validation.tests.annotation.helper_point import contained_in_tomo


@pytest.mark.annotation
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestInstanceSegmentationAnnotations:
    ### BEGIN Self-consistency tests ###
    def test_instance_count_consistent(
        self,
        instance_seg_annotations: Dict[str, List[Dict]],
        annotation_metadata: Dict[str, Dict],
        instance_seg_annotation_files_to_metadata_files: Dict[str, str],
    ):
        """Check that the number of instances is consistent between the metadata (object_count) and the ndjson file (# of unique instance_id)."""
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
    def test_contained_in_tomo(
        self,
        instance_seg_annotations: Dict[str, List[Dict]],
        canonical_tomogram_metadata: Dict,
    ):
        """Check that all points are contained within the tomogram dimensions."""
        contained_in_tomo(instance_seg_annotations, canonical_tomogram_metadata)

    ### END Tomogram-consistency tests ###
