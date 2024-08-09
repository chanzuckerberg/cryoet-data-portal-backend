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

    """Validate the mrc file header for a volume annotation."""

    ### BEGIN MRC Self-consistency tests ###
    def test_is_volume(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the mrc file is a volume."""

        for mrc_filename, interpreter in seg_mask_annotation_mrc_headers.items():
            print(f"MRC File: {mrc_filename}")
            header = interpreter.header
            assert header.ispg == self.VOLUME_SPACEGROUP

    def test_map_id_string(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the MAP ID is correct."""

        for mrc_filename, interpreter in seg_mask_annotation_mrc_headers.items():
            print(f"MRC File: {mrc_filename}")
            header = interpreter.header
            assert header.map == self.MAP_ID

    def test_machine_stamp(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the machine stamp is valid."""

        for mrc_filename, interpreter in seg_mask_annotation_mrc_headers.items():
            print(f"MRC File: {mrc_filename}")
            header = interpreter.header
            try:
                utils.byte_order_from_machine_stamp(header.machst)
            except ValueError:
                pytest.fail(f"Machine stamp is invalid: {utils.pretty_machine_stamp(header.machst)}")

    def test_mrc_mode(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the mrc mode is valid."""

        for mrc_filename, interpreter in seg_mask_annotation_mrc_headers.items():
            print(f"MRC File: {mrc_filename}")
            header = interpreter.header
            try:
                assert utils.dtype_from_mode(header.mode) == np.int8
            except ValueError:
                pytest.fail(f"Mode is invalid: {header.mode}")

    def test_map_dimension_fields(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the map dimension fields are non-negative."""

        for mrc_filename, interpreter in seg_mask_annotation_mrc_headers.items():
            print(f"MRC File: {mrc_filename}")
            header = interpreter.header
            for field in ["nx", "ny", "nz", "mx", "my", "mz", "ispg", "nlabl"]:
                print(f"\t\tField: {header[field]}")
                assert header[field] >= 0

    def test_cell_dimensions(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the cell dimensions are non-negative and match the voxel size."""

        for mrc_filename, interpreter in seg_mask_annotation_mrc_headers.items():
            print(f"MRC File: {mrc_filename}")
            header = interpreter.header
            assert header.cella.x >= 0 and header.cella.x == pytest.approx(
                header.mx * interpreter.voxel_size["x"].astype(float),
            )
            assert header.cella.y >= 0 and header.cella.y == pytest.approx(
                header.my * interpreter.voxel_size["y"].astype(float),
            )
            assert header.cella.z >= 0 and header.cella.z == pytest.approx(
                header.mz * interpreter.voxel_size["z"].astype(float),
            )

    def test_nlabel(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the nlabel is correct."""

        for mrc_filename, interpreter in seg_mask_annotation_mrc_headers.items():
            print(f"MRC File: {mrc_filename}")
            header = interpreter.header
            count = 0
            empty_label = False
            for label in header.label:
                if len(label.strip()) > 0:
                    count += 1

                if len(label) != 0 and len(label.strip()) == 0:
                    empty_label = True

            assert count == header.nlabl
            assert empty_label is False

    def test_nversion(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the nversion is correct."""

        for mrc_filename, interpreter in seg_mask_annotation_mrc_headers.items():
            print(f"MRC File: {mrc_filename}")
            header = interpreter.header
            assert header.nversion in [20140, 20141]

    def test_exttyp(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the exttyp is correct."""

        for mrc_filename, interpreter in seg_mask_annotation_mrc_headers.items():
            print(f"MRC File: {mrc_filename}")
            header = interpreter.header
            if header.nsymbt > 0:
                assert header.exttyp in [b"CCP4", b"MRCO", b"SERI", b"AGAR", b"FEI1", b"FEI2", b"HDF5"]
            assert (
                header.nsymbt == 0
                and interpreter.extended_header is None
                or header.nsymbt == interpreter.extended_header.nbytes
            )

    def test_spacing_consistent(
        self,
        seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter],
        voxel_spacing: float,
    ):
        """Check that the voxel spacing is consistent with the mrc header."""

        for mrc_filename, interpreter in seg_mask_annotation_mrc_headers.items():
            print(f"MRC File: {mrc_filename}")
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

    def test_axis_mapping(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the axis mapping is x == col, y == row, z == sec."""

        for mrc_filename, interpreter in seg_mask_annotation_mrc_headers.items():
            print(f"MRC File: {mrc_filename}")
            header = interpreter.header

            # Standard axis mapping
            assert header.mapc == 1
            assert header.mapr == 2
            assert header.maps == 3

    def test_unit_cell_valid_for_3d_volume(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the unit cell is valid for a volume."""

        for mrc_filename, interpreter in seg_mask_annotation_mrc_headers.items():
            print(f"MRC File: {mrc_filename}")
            header = interpreter.header

            # Unit cell z-size is 1
            assert header.mx == header.nx
            assert header.my == header.ny
            assert header.mz == header.nz

            # Check that the unit cell angles specify cartesian system
            assert header.cellb.alpha == 90
            assert header.cellb.beta == 90
            assert header.cellb.gamma == 90

    def test_origin_is_zero(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the origin is zero."""

        for mrc_filename, interpreter in seg_mask_annotation_mrc_headers.items():
            print(f"MRC File: {mrc_filename}")
            header = interpreter.header

            # Origin is zero
            assert header.origin.x == 0
            assert header.origin.y == 0
            assert header.origin.z == 0

    def test_subimage_start_is_zero(self, seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter]):
        """Check that the subimage start is zero for a volume."""

        for mrc_filename, interpreter in seg_mask_annotation_mrc_headers.items():
            print(f"MRC File: {mrc_filename}")
            header = interpreter.header

            # Subimage start is zero
            assert header.nxstart == 0
            assert header.nystart == 0
            assert header.nzstart == 0

    ### END MRC Self-consistency tests ###

    ### BEGIN ZARR Self-consistency tests ###
    def test_zarr_metadata(
        self,
        seg_mask_annotation_zarr_headers: Dict[str, Dict],
        voxel_spacing,
    ):
        """Check that the path and voxel spacings are correct for a zarr annotation file."""
        for zarr_filename, header_data in seg_mask_annotation_zarr_headers.items():
            print(f"Zarr File: {zarr_filename}")

            zattrs = header_data["zattrs"]
            for i in range(3):
                print(f"\t\tZattrs: {i}")
                datasets_entry = zattrs["multiscales"][0]["datasets"][i]
                assert datasets_entry["path"] == str(i)
                assert datasets_entry["coordinateTransformations"][0]["scale"] == [voxel_spacing * (2**i)] * 3

    def test_zarr_data_type(self, seg_mask_annotation_zarr_headers: Dict[str, Dict]):
        """Check that the data type is correct for a zarr annotation file (int8)."""
        for zarr_filename, header_data in seg_mask_annotation_zarr_headers.items():
            print(f"Zarr File: {zarr_filename}")

            zarrays = header_data["zarrays"]
            for i, zarray in zarrays.items():
                print(f"\t\tZarray: {i}")
                assert np.dtype(zarray["dtype"]) == np.int8

    ### END ZARR Self-consistency tests ###

    ### BEGIN Cross-format consistency tests ###

    def test_zarr_mrc_volume_size(
        self,
        seg_mask_annotation_zarr_headers: Dict[str, Dict],
        seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter],
    ):
        """Check that the zarr volume size matches the mrc volume size, for each zarr annotation file and its binnings."""
        for zarr_filename, header_data in seg_mask_annotation_zarr_headers.items():
            print(f"\tZarr File: {zarr_filename}")
            mrc_file = zarr_filename.replace(".zarr", ".mrc")
            print(f"\tMRC File: {mrc_file}")

            zarrays = header_data["zarrays"]
            for i, zarray in zarrays.items():
                print(f"\t\tZarray: {i}")
                header = seg_mask_annotation_mrc_headers[mrc_file].header
                unbinned_zarray_shape = np.array(zarray["shape"]) * 2**i
                assert (unbinned_zarray_shape == [header.nz, header.ny, header.nx]).all()

    ### END Cross-format consistency tests ###

    ### BEGIN Tomogram-consistency tests ###
    def test_contained_in_tomo(
        self,
        seg_mask_annotation_mrc_headers: Dict[str, MrcInterpreter],
        canonical_tomogram_metadata: Dict,
    ):
        """Check that the annotation volume is contained within the canonical tomogram dimensions."""

        for mrc_filename, interpreter in seg_mask_annotation_mrc_headers.items():
            print(f"MRC File: {mrc_filename}")
            header = interpreter.header
            assert header.nx == canonical_tomogram_metadata["size"]["x"]
            assert header.ny == canonical_tomogram_metadata["size"]["y"]
            assert header.nz == canonical_tomogram_metadata["size"]["z"]

    ### END Tomogram-consistency tests ###
