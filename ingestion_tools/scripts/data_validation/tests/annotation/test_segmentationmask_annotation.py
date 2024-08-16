from typing import Dict

import numpy as np
import pytest
from mrcfile.mrcinterpreter import MrcInterpreter
from tests.helper_mrc import HelperTestMRCHeader

ZATTRS_AXIS_ORDER = ["z", "y", "x"]


# By setting this scope to session, scope="session" fixtures will be reinitialized for each run + voxel_spacing combination
@pytest.mark.annotation
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestSegmentationMask(HelperTestMRCHeader):

    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_header_class_variables(
        self,
        seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter],
    ):
        self.spacegroup = 1  # single 3D volume
        self.mrc_headers = seg_mask_annotation_mrc_headers

    ### BEGIN ZARR Self-consistency tests ###
    def zarr_header_helper(
        self,
        seg_mask_annotation_zarr_headers: Dict[str, Dict[str, Dict]],
        check_func: callable,
        **kwargs,
    ):
        """Helper function to check the header of the zarr file."""
        for zarr_filename, header_data in seg_mask_annotation_zarr_headers.items():
            print(f"Checking {zarr_filename}")
            check_func(header_data, zarr_filename, **kwargs)

    def test_zarr_zattrs_path(
        self,
        seg_mask_annotation_zarr_headers: Dict[str, Dict[str, Dict]],
    ):
        """Check that the path is correct for a zarr annotation file."""

        def check_zattrs_path(header_data, _zarr_filename):
            del _zarr_filename
            for i in range(3):
                assert header_data["zattrs"]["multiscales"][0]["datasets"][i]["path"] == str(i)

        self.zarr_header_helper(seg_mask_annotation_zarr_headers, check_zattrs_path)

    def test_zarr_zattrs_voxel_spacings(
        self,
        seg_mask_annotation_zarr_headers: Dict[str, Dict[str, Dict]],
        voxel_spacing,
    ):
        """Check that the voxel spacings are correct for a zarr annotation file."""

        def check_zattrs_voxel_spacings(header_data, _zarr_filename, voxel_spacing):
            del _zarr_filename
            for i in range(3):
                datasets_entry = header_data["zattrs"]["multiscales"][0]["datasets"][i]
                assert datasets_entry["coordinateTransformations"][0]["scale"] == [voxel_spacing * (2**i)] * 3

        self.zarr_header_helper(
            seg_mask_annotation_zarr_headers,
            check_zattrs_voxel_spacings,
            voxel_spacing=voxel_spacing,
        )

    def test_zarr_zattrs_axes(
        self,
        seg_mask_annotation_zarr_headers: Dict[str, Dict[str, Dict]],
    ):
        """Check that the voxel spacings are correct for a zarr annotation file."""

        def check_zattrs_axes(header_data, _zaar_filename):
            del _zaar_filename
            assert len(header_data["zattrs"]["multiscales"][0]["axes"]) == 3
            for i, axis in enumerate(ZATTRS_AXIS_ORDER):
                assert header_data["zattrs"]["multiscales"][0]["axes"][i] == {
                    "name": axis,
                    "type": "space",
                    "unit": "angstrom",
                }

        self.zarr_header_helper(seg_mask_annotation_zarr_headers, check_zattrs_axes)

    def test_zarr_zarray(self, seg_mask_annotation_zarr_headers: Dict[str, Dict[str, Dict]]):
        """Check that the data type is correct for each binning / scale of the zarr annotation file (int8)."""

        def check_zarray(header_data, _zarr_filename):
            del _zarr_filename
            zarrays = header_data["zarrays"]
            assert len(zarrays) == 3
            for zarray in zarrays.values():
                assert np.dtype(zarray["dtype"]) == np.int8

        self.zarr_header_helper(seg_mask_annotation_zarr_headers, check_zarray)

    ### END ZARR Self-consistency tests ###

    ### BEGIN Cross-format consistency tests ###
    def test_zarr_mrc_both_exist(
        self,
        seg_mask_annotation_zarr_headers: Dict[str, Dict[str, Dict]],
        seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter],
    ):
        """Check that both the zarr and mrc annotation files exist for each annotation file."""
        zarr_files = set(seg_mask_annotation_zarr_headers.keys())
        mrc_files = set(seg_mask_annotation_mrc_headers.keys())
        assert {f.replace(".zarr", ".mrc") for f in zarr_files} == mrc_files

    def test_zarr_mrc_volume_size(
        self,
        seg_mask_annotation_zarr_headers: Dict[str, Dict[str, Dict]],
        seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter],
    ):
        """Check that the zarr volume size matches the mrc volume size, for each zarr annotation file and its binnings."""

        def check_volume_size(header_data, zarr_filename):
            mrc_file = zarr_filename.replace(".zarr", ".mrc")

            zarrays = header_data["zarrays"]
            for i, zarray in zarrays.items():
                header = seg_mask_annotation_mrc_headers[mrc_file].header
                unbinned_zarray_shape = np.array(zarray["shape"]) * 2**i
                assert (unbinned_zarray_shape == [header.nz, header.ny, header.nx]).all()

        self.zarr_header_helper(seg_mask_annotation_zarr_headers, check_volume_size)

    ### END Cross-format consistency tests ###

    ### BEGIN Voxel-spacing tests ###
    def test_spacing_consistent(self, voxel_spacing: float):
        """Check that the voxel spacing is consistent with the mrc header."""

        def check_spacing(_header, interpreter, _mrc_filename, voxel_spacing):
            del _header, _mrc_filename
            assert voxel_spacing == pytest.approx(
                interpreter.voxel_size["x"].astype(float),
                abs=self.spacing_tolerance,
            )
            assert voxel_spacing == pytest.approx(
                interpreter.voxel_size["y"].astype(float),
                abs=self.spacing_tolerance,
            )
            assert voxel_spacing == pytest.approx(
                interpreter.voxel_size["z"].astype(float),
                abs=self.spacing_tolerance,
            )

        self.mrc_header_helper(check_spacing, voxel_spacing=voxel_spacing)

    ### END Voxel-spacing tests ###

    ### BEGIN Tomogram-consistency tests ###
    def test_contained_in_tomo(self, canonical_tomogram_metadata: Dict):
        """Check that the annotation volume is contained within the canonical tomogram dimensions."""

        def check_contained_in_tomo(header, _interpreter, _mrc_filename, tomogram_metadata):
            del _interpreter, _mrc_filename
            assert header.nx == tomogram_metadata["size"]["x"]
            assert header.ny == tomogram_metadata["size"]["y"]
            assert header.nz == tomogram_metadata["size"]["z"]

        self.mrc_header_helper(check_contained_in_tomo, tomogram_metadata=canonical_tomogram_metadata)

    ### END Tomogram-consistency tests ###
