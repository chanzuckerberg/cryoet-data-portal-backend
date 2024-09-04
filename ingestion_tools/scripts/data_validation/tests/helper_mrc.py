import warnings
from typing import Dict

import allure
import numpy as np
import pytest
from mrcfile import utils
from mrcfile.mrcinterpreter import MrcInterpreter

from common.fs import S3Filesystem

SPACING_TOLERANCE = 0.001
# 1 MB
DISK_STORAGE_TOLERANCE = 2**20

# Used so that other classes that skip the pytest still have a title in the allure report
# Without repeating the allure title text in every skipped test
MRC_ALLURE_TITLES = {
    "test_is_volume": "MRC: spacegroup (volume type) is correct.",
    "test_map_id_string": "MRC: filetype (MAP ID) is correct.",
    "test_machine_stamp": "MRC: machine stamp is valid.",
    "test_datatype": "MRC: mode (datatype) is valid.",
    "test_map_dimension_fields": "MRC: map dimension fields are non-negative.",
    "test_cell_dimensions": "MRC: cell dimensions are non-negative and match the voxel size.",
    "test_nlabel": "MRC: labels are non-empty and match the nlabl field.",
    "test_nversion": "MRC: nversion is correct.",
    "test_exttyp": "MRC: extended header is valid.",
    "test_axis_mapping": "MRC: has valid axis mapping.",
    "test_unit_cell_valid_for_3d_volume": "MRC: unit cell is valid for a volume.",
    "test_origin_is_zero": "MRC: origin is zero.",
    "test_subimage_start_is_zero": "MRC: subimage start is zero.",
    "test_mrc_spacing": "MRC: voxel spacing is non-negative and matches spacing.",
}


def mrc_allure_title(func):
    """Decorator to automatically set the allure title to the function name."""
    return allure.title(MRC_ALLURE_TITLES.get(func.__name__, func.__name__))(func)


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
    permitted_mrc_datatypes: list = [np.int8, np.int16, np.float32, np.float64]

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

    @mrc_allure_title
    def test_is_volume(self):
        def check_is_volume(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            assert header.ispg == self.spacegroup

        self.mrc_header_helper(check_is_volume)

    @mrc_allure_title
    def test_map_id_string(self):
        def check_map_id(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            assert header.map == self.map_id

        self.mrc_header_helper(check_map_id)

    @mrc_allure_title
    def test_machine_stamp(self):
        def check_machine_stamp(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            try:
                utils.byte_order_from_machine_stamp(header.machst)
            except ValueError as e:
                raise AssertionError(f"Machine stamp is invalid: {utils.pretty_machine_stamp(header.machst)}") from e

        self.mrc_header_helper(check_machine_stamp)

    @mrc_allure_title
    def test_datatype(self):
        def check_datatype(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            assert utils.dtype_from_mode(header.mode) in self.permitted_mrc_datatypes

        self.mrc_header_helper(check_datatype)

    @mrc_allure_title
    def test_map_dimension_fields(self):
        def check_map_dimension_fields(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            for field in ["nx", "ny", "nz", "mx", "my", "mz", "ispg", "nlabl"]:
                assert header[field] >= 0

        self.mrc_header_helper(check_map_dimension_fields)

    @mrc_allure_title
    def test_cell_dimensions(self):
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

    @mrc_allure_title
    def test_nlabel(self):
        def check_nlabel(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            count = sum(1 for label in header.label if label.strip())
            empty_label = any(len(label) != 0 and not label.strip() for label in header.label)

            assert count == header.nlabl
            assert not empty_label

        self.mrc_header_helper(check_nlabel)

    @mrc_allure_title
    def test_nversion(self):
        def check_nversion(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            assert header.nversion in [20140, 20141]

        self.mrc_header_helper(check_nversion)

    @mrc_allure_title
    def test_exttyp(self):
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

    @mrc_allure_title
    def test_axis_mapping(self):
        def check_axis_mapping(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            # Standard axis mapping
            assert header.mapc == 1
            assert header.mapr == 2
            assert header.maps == 3

        self.mrc_header_helper(check_axis_mapping)

    @mrc_allure_title
    def test_unit_cell_valid_for_3d_volume(self):
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

    @mrc_allure_title
    def test_origin_is_zero(self):
        def check_origin(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            # Origin is zero
            assert header.origin.x == 0
            assert header.origin.y == 0
            assert header.origin.z == 0

        self.mrc_header_helper(check_origin)

    @mrc_allure_title
    def test_subimage_start_is_zero(self):
        def check_subimage_start(header, _interpreter, _mrc_filename):
            del _interpreter, _mrc_filename
            # Subimage start is zero
            assert header.nxstart == 0
            assert header.nystart == 0
            assert header.nzstart == 0

        self.mrc_header_helper(check_subimage_start)

    @mrc_allure_title
    def test_disk_storage(self, filesystem: S3Filesystem):
        def check_disk_storage(header, _interpreter, mrc_filename, filesystem: S3Filesystem):
            del _interpreter
            if not mrc_filename.endswith(".mrc"):
                pytest.skip("Only checking disk storage for .mrc files (not compressed files)")

            # volume size + extended header size + header size (1024 bytes)
            expected_bytes = (
                header.nx * header.ny * header.nz * utils.dtype_from_mode(header.mode).itemsize + header.nsymbt + 1024
            )
            actual_bytes = filesystem.s3fs.size(mrc_filename)
            if actual_bytes != expected_bytes:
                warnings.warn(f"Expected {expected_bytes} bytes, got {actual_bytes} bytes", stacklevel=2)
            assert abs(expected_bytes - filesystem.s3fs.size(mrc_filename)) < DISK_STORAGE_TOLERANCE

        self.mrc_header_helper(check_disk_storage, filesystem=filesystem)

    ### BEGIN Voxel-spacing tests ###
    @mrc_allure_title
    def test_mrc_spacing(self):
        def check_spacing(_header, interpreter, _mrc_filename):
            del _header, _mrc_filename
            assert interpreter.voxel_size["x"] == pytest.approx(self.spacing, abs=SPACING_TOLERANCE)
            assert interpreter.voxel_size["y"] == pytest.approx(self.spacing, abs=SPACING_TOLERANCE)
            assert interpreter.voxel_size["z"] == pytest.approx(self.spacing, abs=SPACING_TOLERANCE)

        self.mrc_header_helper(check_spacing)

    ### END Voxel-spacing tests ###
