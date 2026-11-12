from typing import Dict

import allure
import numpy as np
import pytest
from data_validation.shared.helper.helper_mrc_zarr import HelperTestMRCZarrHeader
from mrcfile.mrcinterpreter import MrcInterpreter


# By setting this scope to session, scope="session" fixtures will be reinitialized for each run + voxel_spacing combination
@pytest.mark.annotation
@pytest.mark.parametrize("dataset, run_name, voxel_spacing", pytest.cryoet.dataset_run_spacing_combinations, scope="session")
class TestSegmentationMask(HelperTestMRCZarrHeader):

    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_zarr_header_class_variables(
        self,
        seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter],
        seg_mask_annotation_zarr_headers: Dict[str, Dict[str, Dict]],
        voxel_spacing: str,
        seg_mask_annotation_files_to_metadata: Dict,
        seg_mask_annotation_mrc_files_to_metadata_files: Dict[str, str],
    ):
        # keyed by the masks' zarr files: determines whether these tests should be skipped or ran
        del seg_mask_annotation_files_to_metadata
        # The MRC files the metadata lists (checked to exist, with no others present). Masks ingested with --skip-mrc
        # list none: the MRC checks are skipped for them.
        self.expected_mrc_files = set(seg_mask_annotation_mrc_files_to_metadata_files)
        self.error_on_no_mrc_header = bool(self.expected_mrc_files)
        self.spacegroup = 1  # single 3D volume
        self.mrc_headers = seg_mask_annotation_mrc_headers
        self.zarr_headers = seg_mask_annotation_zarr_headers
        self.spacing = float(voxel_spacing)
        self.permitted_zarr_datatypes = [np.int8]

    ### BEGIN Tomogram-consistency tests ###
    @allure.title("Segmentation mask: volumes are contained within the tomogram dimensions.")
    def test_contained_in_tomo(self, seg_mask_annotation_files_to_metadata: Dict, all_vs_tomogram_metadata: Dict):
        # Level 0 of the mask's zarr (every mask has one; the MRC is optional) must have the tomogram's size. The MRC,
        # where there is one, has the zarr's level-0 size (test_zarr_mrc_volume_size).
        tomo_metadata = {}
        for filename, metadata in seg_mask_annotation_files_to_metadata.items():
            for tomo_data in all_vs_tomogram_metadata:
                if metadata["alignment_metadata_path"] == tomo_data["alignment_metadata_path"]:
                    tomo_metadata[filename] = tomo_data
                    break

        def check_contained_in_tomo(header_data, zarr_filename, tomogram_metadata):
            this_tomo_metadata = tomogram_metadata[zarr_filename]
            z, y, x = header_data["zarrays"][0]["shape"][-3:]
            assert x == this_tomo_metadata["size"]["x"]
            assert y == this_tomo_metadata["size"]["y"]
            assert z == this_tomo_metadata["size"]["z"]

        self.zarr_header_helper(check_contained_in_tomo, tomogram_metadata=tomo_metadata)

    ### END Tomogram-consistency tests ###
