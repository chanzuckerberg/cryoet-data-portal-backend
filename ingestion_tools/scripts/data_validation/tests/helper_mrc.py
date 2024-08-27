from typing import Dict

import numpy as np
import pytest
from mrcfile import utils
from mrcfile.mrcinterpreter import MrcInterpreter

SPACING_TOLERANCE = 0.001


class HelperTestMRCHeader:
    """
    This is a helper class that containts pytests for checking the header of an mrc file.
    This class itself is not labeled as a pytest test class (why it starts Helper instead of Test), because
    we don't want to run these tests directly. Instead, this class is inherited by a class that is labeled
    as a pytest test class, and that class will run the tests in this class. In the pytest class, we will
    also set the class variables that are required by this class.
    """

    # Class variables that need to be set by the subclass
    map_id: bytes = b"MAP "
    spacegroup: int = None
    mrc_headers: Dict[str, MrcInterpreter] = None
    spacing: float = None
    skip_z_axis_checks: bool = False

    def mrc_header_helper(
        self,
        check_func: callable,
        **kwargs,
    ):
        """Helper function to check the header of the mrc file. Used by all the test classes to stay DRY."""
        if not self.mrc_headers:
            pytest.skip("No mrc headers to check")

        for mrc_filename, interpreter in self.mrc_headers.items():
            print(f"Checking {mrc_filename}")
            check_func(interpreter.header, interpreter, mrc_filename, **kwargs)

    def test_is_volume(self):
        """Check that the mrc file is a volume."""

        def check_is_volume(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            assert header.ispg == self.spacegroup

        self.mrc_header_helper(check_is_volume)

    def test_map_id_string(self):
        """Check that the MAP ID is correct."""

        def check_map_id(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            assert header.map == self.map_id

        self.mrc_header_helper(check_map_id)

    def test_machine_stamp(self):
        """Check that the machine stamp is valid."""

        def check_machine_stamp(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            try:
                utils.byte_order_from_machine_stamp(header.machst)
            except ValueError as e:
                raise AssertionError(f"Machine stamp is invalid: {utils.pretty_machine_stamp(header.machst)}") from e

        self.mrc_header_helper(check_machine_stamp)

    def test_mrc_mode(self):
        """Check that the mrc mode (dtype) is valid."""

        def check_mrc_mode(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            assert utils.dtype_from_mode(header.mode) in [np.int8, np.float32]

        self.mrc_header_helper(check_mrc_mode)

    def test_map_dimension_fields(self):
        """Check that the map dimension fields are non-negative."""

        def check_map_dimension_fields(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            for field in ["nx", "ny", "nz", "mx", "my", "mz", "ispg", "nlabl"]:
                assert header[field] >= 0

        self.mrc_header_helper(check_map_dimension_fields)

    def test_cell_dimensions(self):
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

        self.mrc_header_helper(check_cell_dimensions)

    def test_nlabel(self):
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

        self.mrc_header_helper(check_nlabel)

    def test_nversion(self):
        """Check that the nversion is correct."""

        def check_nversion(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            assert header.nversion in [20140, 20141]

        self.mrc_header_helper(check_nversion)

    def test_exttyp(self):
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

        self.mrc_header_helper(check_exttyp)

    def test_axis_mapping(self):
        """Check that the axis mapping is x == col, y == row, z == sec."""

        def check_axis_mapping(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            # Standard axis mapping
            assert header.mapc == 1
            assert header.mapr == 2
            assert header.maps == 3

        self.mrc_header_helper(check_axis_mapping)

    def test_unit_cell_valid_for_3d_volume(self):
        """Check that the unit cell is valid for a volume."""

        def check_unit_cell(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            # Unit cell z-size is 1
            assert header.mx == header.nx
            assert header.my == header.ny
            assert header.mz == 1 if self.skip_z_axis_checks else header.mz == header.nz

            # Check that the unit cell angles specify cartesian system
            assert header.cellb.alpha == 90
            assert header.cellb.beta == 90
            assert header.cellb.gamma == 90

        self.mrc_header_helper(check_unit_cell)

    def test_origin_is_zero(self):
        """Check that the origin is zero."""

        def check_origin(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            # Origin is zero
            assert header.origin.x == 0
            assert header.origin.y == 0
            assert header.origin.z == 0

        self.mrc_header_helper(check_origin)

    def test_subimage_start_is_zero(self):
        """Check that the subimage start is zero for a volume."""

        def check_subimage_start(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            # Subimage start is zero
            assert header.nxstart == 0
            assert header.nystart == 0
            assert header.nzstart == 0

        self.mrc_header_helper(check_subimage_start)

    ### BEGIN Voxel-spacing tests ###
    def test_mrc_spacing(self):
        """Check that the voxel / pixel spacing is consistent with the mrc header."""

        def check_spacing(_header, interpreter, _mrc_filename):
            del _header, _mrc_filename
            assert interpreter.voxel_size["x"] == pytest.approx(self.spacing, abs=SPACING_TOLERANCE)
            assert interpreter.voxel_size["y"] == pytest.approx(self.spacing, abs=SPACING_TOLERANCE)
            assert interpreter.voxel_size["z"] == pytest.approx(self.spacing, abs=SPACING_TOLERANCE)

        self.mrc_header_helper(check_spacing)

    ### END Voxel-spacing tests ###
