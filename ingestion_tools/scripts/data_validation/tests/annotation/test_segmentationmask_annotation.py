from typing import Dict

import allure
import numpy as np
import pytest
from data_validation.tests.helper_mrc_zarr import HelperTestMRCZarrHeader
from mrcfile.mrcinterpreter import MrcInterpreter


# By setting this scope to session, scope="session" fixtures will be reinitialized for each run + voxel_spacing combination
@pytest.mark.annotation
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestSegmentationMask(HelperTestMRCZarrHeader):

    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_zarr_header_class_variables(
        self,
        seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter],
        seg_mask_annotation_zarr_headers: Dict[str, Dict[str, Dict]],
        voxel_spacing: str,
    ):
        self.spacegroup = 1  # single 3D volume
        self.mrc_headers = seg_mask_annotation_mrc_headers
        self.zarr_headers = seg_mask_annotation_zarr_headers
        self.spacing = float(voxel_spacing)
        self.permitted_zarr_datatypes = [np.int8]

    ### BEGIN Tomogram-consistency tests ###
    @allure.title("Segmentation mask: volumes are contained within the tomogram dimensions.")
    def test_contained_in_tomo(self, tomogram_metadata: Dict):
        def check_contained_in_tomo(header, _interpreter, _mrc_filename, tomogram_metadata):
            del _interpreter, _mrc_filename
            assert header.nx == tomogram_metadata["size"]["x"]
            assert header.ny == tomogram_metadata["size"]["y"]
            assert header.nz == tomogram_metadata["size"]["z"]

        self.mrc_header_helper(check_contained_in_tomo, tomogram_metadata=tomogram_metadata)

    ### END Tomogram-consistency tests ###
