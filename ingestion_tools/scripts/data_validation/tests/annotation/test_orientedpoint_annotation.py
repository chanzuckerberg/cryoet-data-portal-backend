from typing import Dict, List

import allure
import numpy as np
import pytest
from data_validation.tests.annotation.helper_point import contained_in_tomo, point_count_consistent


@pytest.mark.annotation
@pytest.mark.parametrize("dataset, run_name, voxel_spacing", pytest.dataset_run_spacing_combinations, scope="session")
class TestOrientedPointAnnotations:
    ### BEGIN Self-consistency tests ###

    @allure.title("Oriented point: number of annotations is consistent between metadata and ndjson file.")
    def test_point_count_consistent(
        self,
        oriented_point_annotations: Dict[str, List[Dict]],
        annotation_metadata: Dict[str, Dict],
        oriented_point_annotation_files_to_metadata_files: Dict[str, str],
    ):
        point_count_consistent(
            oriented_point_annotations,
            annotation_metadata,
            oriented_point_annotation_files_to_metadata_files,
        )

    def valid_rotation_matrix(self, matrix: List[List[float]]) -> bool:
        """
        Check that the rotation matrix is 3x3 and has a determinant of 1.
        Also that each row is a unit vector and the rows are orthogonal.
        """
        np_matrix = np.array(matrix)
        assert np_matrix.shape == (3, 3)
        assert np.isclose(np.linalg.det(np_matrix), 1.0)
        assert np.allclose(np.linalg.norm(np_matrix, axis=1), 1.0)
        # If all rows are orthogonal, then the dot product of the matrix and its transpose should be the identity matrix.
        assert np.allclose(np.dot(np_matrix, np_matrix.T), np.eye(3))

    @allure.title("Oriented point: valid rotation matrix.")
    @allure.description(
        "The rotation matrix should be 3x3, have a determinant of 1, and have row orthogonal unit vectors.",
    )
    def test_rotation_matrix(self, oriented_point_annotations: Dict[str, List[Dict]]):
        for annotation_filename, points in oriented_point_annotations.items():
            print(f"\tFile: {annotation_filename}")
            for point in points:
                self.valid_rotation_matrix(point["xyz_rotation_matrix"])

    ### END Self-consistency tests ###

    ### BEGIN Tomogram-consistency tests ###
    @allure.title("Oriented point: contained within the tomogram dimensions.")
    def test_contained_in_tomo(
        self,
        oriented_point_annotations: Dict[str, List[Dict]],
        tomogram_metadata: Dict,
    ):
        contained_in_tomo(oriented_point_annotations, tomogram_metadata)

    ### END Tomogram-consistency tests ###
