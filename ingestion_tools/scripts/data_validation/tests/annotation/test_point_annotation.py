from typing import Dict

import pytest
from helpers_point import contained_in_tomo, point_count_consistent


@pytest.mark.annotation
@pytest.mark.metadata
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestPointAnnotations:
    ### BEGIN Self-consistency tests ###
    def test_point_count_consistent(
        self,
        point_annotations: Dict[str, Dict[str, Dict]],
        annotation_metadata: Dict[str, Dict],
    ):
        """Check that the number of annotations is consistent between the metadata and the ndjson file."""
        point_count_consistent(point_annotations, annotation_metadata)

    ### END Self-consistency tests ###

    ### BEGIN Tomogram-consistency tests ###
    def test_contained_in_tomo(self, point_annotations: Dict[str, Dict[str, Dict]], canonical_tomogram_metadata: Dict):
        """Check that all points are contained within the tomogram dimensions."""
        contained_in_tomo(point_annotations, canonical_tomogram_metadata)

    ### END Tomogram-consistency tests ###
