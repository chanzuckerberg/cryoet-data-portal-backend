from typing import Dict

import numpy as np
import pytest
from mrcfile import utils
from mrcfile.mrcinterpreter import MrcInterpreter


# By setting this scope to session, scope="session" fixtures will be reinitialized for each run + voxel_spacing combination
@pytest.mark.annotation
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestSegmentationMaskHeader:
    MAP_ID = b"MAP "
    VOLUME_SPACEGROUP = 1
    # Tolerance for voxel spacing assertions
    SPACING_TOLERANCE = 0.01
    ZATTRS_AXIS_ORDER = ["z", "y", "x"]

    """Validate the mrc file header for a volume annotation."""

    ### BEGIN MRC Self-consistency tests ###
    def mrc_header_helper(
        self,
        seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter],
        check_func: callable,
        **kwargs,
    ):
        """Helper function to check the header of the mrc file."""
        for mrc_filename, interpreter in seg_mask_annotation_mrc_headers.items():
            print(f"Checking {mrc_filename}")
            try:
                check_func(interpreter.header, interpreter, mrc_filename, **kwargs)
            except Exception as e:
                pytest.fail(f"Error in file {mrc_filename}, with kwargs {kwargs}: {e}")

    def test_is_volume(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the mrc file is a volume."""

        def check_is_volume(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            assert header.ispg == self.VOLUME_SPACEGROUP

        self.mrc_header_helper(seg_mask_annotation_mrc_headers, check_is_volume)

    def test_map_id_string(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the MAP ID is correct."""

        def check_map_id(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            assert header.map == self.MAP_ID

        self.mrc_header_helper(seg_mask_annotation_mrc_headers, check_map_id)

    def test_machine_stamp(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the machine stamp is valid."""

        def check_machine_stamp(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            try:
                utils.byte_order_from_machine_stamp(header.machst)
            except ValueError as e:
                raise AssertionError(f"Machine stamp is invalid: {utils.pretty_machine_stamp(header.machst)}") from e

        self.mrc_header_helper(seg_mask_annotation_mrc_headers, check_machine_stamp)

    def test_mrc_mode(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the mrc mode is valid."""

        def check_mrc_mode(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            assert utils.dtype_from_mode(header.mode) == np.int8

        self.mrc_header_helper(seg_mask_annotation_mrc_headers, check_mrc_mode)

    def test_map_dimension_fields(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the map dimension fields are non-negative."""

        def check_map_dimension_fields(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            for field in ["nx", "ny", "nz", "mx", "my", "mz", "ispg", "nlabl"]:
                assert header[field] >= 0

        self.mrc_header_helper(seg_mask_annotation_mrc_headers, check_map_dimension_fields)

    def test_cell_dimensions(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the cell dimensions are non-negative and match the voxel size."""

        def check_cell_dimensions(header, interpreter, _mrc_filename):
            del _mrc_filename
            assert header.cella.x >= 0 and header.cella.x == pytest.approx(
                header.mx * interpreter.voxel_size["x"].astype(float),
            )
            assert header.cella.y >= 0 and header.cella.y == pytest.approx(
                header.my * interpreter.voxel_size["y"].astype(float),
            )
            assert header.cella.z >= 0 and header.cella.z == pytest.approx(
                header.mz * interpreter.voxel_size["z"].astype(float),
            )

        self.mrc_header_helper(seg_mask_annotation_mrc_headers, check_cell_dimensions)

    def test_nlabel(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the nlabel is correct."""

        def check_nlabel(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            count = 0
            empty_label = False
            for label in header.label:
                if len(label.strip()) > 0:
                    count += 1

                if len(label) != 0 and len(label.strip()) == 0:
                    empty_label = True

            assert count == header.nlabl
            assert empty_label is False

        self.mrc_header_helper(seg_mask_annotation_mrc_headers, check_nlabel)

    def test_nversion(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the nversion is correct."""

        def check_nversion(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            assert header.nversion in [20140, 20141]

        self.mrc_header_helper(seg_mask_annotation_mrc_headers, check_nversion)

    def test_exttyp(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the exttyp is correct."""

        def check_exttyp(header, interpreter, _mrc_filename):
            del _mrc_filename
            if header.nsymbt > 0:
                assert header.exttyp in [b"CCP4", b"MRCO", b"SERI", b"AGAR", b"FEI1", b"FEI2", b"HDF5"]
            assert (
                header.nsymbt == 0
                and interpreter.extended_header is None
                or header.nsymbt == interpreter.extended_header.nbytes
            )

        self.mrc_header_helper(seg_mask_annotation_mrc_headers, check_exttyp)

    def test_spacing_consistent(
        self,
        seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter],
        voxel_spacing: float,
    ):
        """Check that the voxel spacing is consistent with the mrc header."""

        def check_spacing(_header, interpreter, _mrc_filename, voxel_spacing):
            del _header, _mrc_filename
            assert voxel_spacing == pytest.approx(
                interpreter.voxel_size["x"].astype(float),
                abs=self.SPACING_TOLERANCE,
            )
            assert voxel_spacing == pytest.approx(
                interpreter.voxel_size["y"].astype(float),
                abs=self.SPACING_TOLERANCE,
            )
            assert voxel_spacing == pytest.approx(
                interpreter.voxel_size["z"].astype(float),
                abs=self.SPACING_TOLERANCE,
            )

        self.mrc_header_helper(seg_mask_annotation_mrc_headers, check_spacing, voxel_spacing=voxel_spacing)

    def test_axis_mapping(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the axis mapping is x == col, y == row, z == sec."""

        def check_axis_mapping(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            # Standard axis mapping
            assert header.mapc == 1
            assert header.mapr == 2
            assert header.maps == 3

        self.mrc_header_helper(seg_mask_annotation_mrc_headers, check_axis_mapping)

    def test_unit_cell_valid_for_3d_volume(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the unit cell is valid for a volume."""

        def check_unit_cell(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            # Unit cell z-size is 1
            assert header.mx == header.nx
            assert header.my == header.ny
            assert header.mz == header.nz

            # Check that the unit cell angles specify cartesian system
            assert header.cellb.alpha == 90
            assert header.cellb.beta == 90
            assert header.cellb.gamma == 90

        self.mrc_header_helper(seg_mask_annotation_mrc_headers, check_unit_cell)

    def test_origin_is_zero(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the origin is zero."""

        def check_origin(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            # Origin is zero
            assert header.origin.x == 0
            assert header.origin.y == 0
            assert header.origin.z == 0

        self.mrc_header_helper(seg_mask_annotation_mrc_headers, check_origin)

    def test_subimage_start_is_zero(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the subimage start is zero for a volume."""

        def check_subimage_start(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            # Subimage start is zero
            assert header.nxstart == 0
            assert header.nystart == 0
            assert header.nzstart == 0

        self.mrc_header_helper(seg_mask_annotation_mrc_headers, check_subimage_start)

    ### END MRC Self-consistency tests ###

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
            try:
                check_func(header_data, zarr_filename, **kwargs)
            except Exception as e:
                pytest.fail(f"Error in file {zarr_filename}, with kwargs {kwargs}: {e}")

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
            for i, axis in enumerate(self.ZATTRS_AXIS_ORDER):
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

    ### BEGIN Tomogram-consistency tests ###
    def test_contained_in_tomo(
        self,
        seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter],
        canonical_tomogram_metadata: Dict,
    ):
        """Check that the annotation volume is contained within the canonical tomogram dimensions."""

        def check_contained_in_tomo(header, _interpreter, _mrc_filename, canonical_tomogram_metadata):
            del _interpreter, _mrc_filename
            assert header.nx == canonical_tomogram_metadata["size"]["x"]
            assert header.ny == canonical_tomogram_metadata["size"]["y"]
            assert header.nz == canonical_tomogram_metadata["size"]["z"]

        self.mrc_header_helper(
            seg_mask_annotation_mrc_headers,
            check_contained_in_tomo,
            canonical_tomogram_metadata=canonical_tomogram_metadata,
        )

    ### END Tomogram-consistency tests ###
