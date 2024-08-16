from typing import Dict, List

import pytest
from helper_point import contained_in_tomo, point_count_consistent


@pytest.mark.annotation
@pytest.mark.metadata
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestPointAnnotations:
    ### BEGIN Self-consistency tests ###
    def test_point_count_consistent(
        self,
        point_annotations: Dict[str, List[Dict]],
        annotation_metadata: Dict[str, Dict],
        point_annotation_files_to_metadata_files: Dict[str, str],
    ):
        """Check that the number of annotations is consistent between the metadata and the ndjson file."""
        point_count_consistent(point_annotations, annotation_metadata, point_annotation_files_to_metadata_files)

    ### END Self-consistency tests ###

    ### BEGIN Tomogram-consistency tests ###
    def test_contained_in_tomo(
        self,
        point_annotations: Dict[str, List[Dict]],
        canonical_tomogram_metadata: Dict,
    ):
        """Check that all points are contained within the tomogram dimensions."""
        contained_in_tomo(point_annotations, canonical_tomogram_metadata)

    ### END Tomogram-consistency tests ###
