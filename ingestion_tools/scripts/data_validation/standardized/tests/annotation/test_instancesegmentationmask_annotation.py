from typing import Dict

import allure
import numpy as np
import pytest
from data_validation.shared.helper.helper_mrc_zarr import HelperTestMRCZarrHeader
from mrcfile.mrcinterpreter import MrcInterpreter


# By setting this scope to session, scope="session" fixtures will be reinitialized for each run + voxel_spacing combination
@pytest.mark.annotation
@pytest.mark.parametrize("dataset, run_name, voxel_spacing", pytest.cryoet.dataset_run_spacing_combinations, scope="session")
class TestInstanceSegmentationMask(HelperTestMRCZarrHeader):

    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_zarr_header_class_variables(
        self,
        instance_seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter],
        instance_seg_mask_annotation_zarr_headers: Dict[str, Dict[str, Dict]],
        voxel_spacing: str,
        instance_seg_mask_annotation_files_to_metadata: Dict,
    ):
        # unused for now, kept since this fixture determines whether these tests should be skipped or ran
        del instance_seg_mask_annotation_files_to_metadata
        self.spacegroup = 1  # single 3D volume
        self.mrc_headers = instance_seg_mask_annotation_mrc_headers
        self.zarr_headers = instance_seg_mask_annotation_zarr_headers
        self.spacing = float(voxel_spacing)
        # MultiLabelMaskConverter always produces uint16 (MRC mode 6).
        self.permitted_mrc_datatypes = [np.uint16]
        self.permitted_zarr_datatypes = [np.uint16]

    ### BEGIN Tomogram-consistency tests ###
    @allure.title("Instance segmentation mask: volumes are contained within the tomogram dimensions.")
    def test_contained_in_tomo(self, instance_seg_mask_annotation_files_to_metadata: Dict, all_vs_tomogram_metadata: Dict):
        tomo_metadata = {}
        for filename, metadata in instance_seg_mask_annotation_files_to_metadata.items():
            for tomo_data in all_vs_tomogram_metadata:
                if metadata["alignment_metadata_path"] == tomo_data["alignment_metadata_path"]:
                    tomo_metadata[filename] = tomo_data
                    break

        def check_contained_in_tomo(header, _interpreter, _mrc_filename, tomogram_metadata):
            this_tomo_metadata = tomo_metadata[_mrc_filename]
            del _interpreter, _mrc_filename
            assert header.nx == this_tomo_metadata["size"]["x"]
            assert header.ny == this_tomo_metadata["size"]["y"]
            assert header.nz == this_tomo_metadata["size"]["z"]

        self.mrc_header_helper(check_contained_in_tomo, tomogram_metadata=tomo_metadata)

    ### END Tomogram-consistency tests ###

    ### BEGIN Instance segmentation mask-specific zarr metadata tests ###
    @allure.title("Instance segmentation mask: zarr image-label metadata exists with valid label entries.")
    @allure.description(
        "Instance segmentation mask zarr files should contain image-label metadata in zattrs "
        "with a list of label-value entries, all of which must be positive integers (0 is background).",
    )
    def test_zarr_image_label_metadata(self):
        def check_image_label_metadata(header_data, zarr_filename):
            zattrs = header_data["zattrs"]
            multiscales_metadata = zattrs.get("multiscales", [{}])[0].get("metadata", {})
            image_label = multiscales_metadata.get("image-label")
            assert image_label is not None, (
                f"{zarr_filename}: missing 'image-label' in zarr multiscales metadata"
            )
            assert "colors" in image_label, (
                f"{zarr_filename}: 'image-label' metadata missing 'colors' field"
            )
            colors = image_label["colors"]
            assert len(colors) > 0, (
                f"{zarr_filename}: 'image-label' colors list is empty (no instance labels found)"
            )
            for entry in colors:
                assert "label-value" in entry, (
                    f"{zarr_filename}: label entry missing 'label-value' key: {entry}"
                )
                label = entry["label-value"]
                assert isinstance(label, int) and label > 0, (
                    f"{zarr_filename}: label-value must be a positive integer, got {label}"
                )

        self.zarr_header_helper(check_image_label_metadata)

    @allure.title("Instance segmentation mask: zarr image-label values are unique.")
    @allure.description(
        "All label-value entries in the zarr image-label metadata should be unique "
        "(no duplicate instance IDs).",
    )
    def test_zarr_labels_unique(self):
        def check_labels_unique(header_data, zarr_filename):
            zattrs = header_data["zattrs"]
            multiscales_metadata = zattrs.get("multiscales", [{}])[0].get("metadata", {})
            image_label = multiscales_metadata.get("image-label")
            if image_label is None:
                return

            labels = [entry["label-value"] for entry in image_label["colors"]]
            assert len(labels) == len(set(labels)), (
                f"{zarr_filename}: duplicate label-values found in image-label metadata: {labels}"
            )

        self.zarr_header_helper(check_labels_unique)

    @allure.title("Instance segmentation mask: label count matches annotation metadata object_count.")
    @allure.description(
        "The number of unique instance labels stored in the zarr image-label metadata "
        "should match the object_count from the annotation metadata.",
    )
    def test_label_count_matches_metadata(self, instance_seg_mask_annotation_files_to_metadata: Dict):
        for zarr_filename, header_data in self.zarr_headers.items():
            zattrs = header_data["zattrs"]
            multiscales_metadata = zattrs.get("multiscales", [{}])[0].get("metadata", {})
            image_label = multiscales_metadata.get("image-label")
            if image_label is None:
                continue

            mrc_filename = zarr_filename.replace(".zarr", ".mrc")
            if mrc_filename not in instance_seg_mask_annotation_files_to_metadata:
                continue

            annotation_metadata = instance_seg_mask_annotation_files_to_metadata[mrc_filename]
            expected_count = annotation_metadata.get("object_count")
            if expected_count is None:
                continue

            actual_count = len(image_label["colors"])
            assert actual_count == expected_count, (
                f"{zarr_filename}: zarr image-label has {actual_count} labels, "
                f"but annotation metadata object_count is {expected_count}"
            )

    ### END Instance segmentation mask-specific zarr metadata tests ###
