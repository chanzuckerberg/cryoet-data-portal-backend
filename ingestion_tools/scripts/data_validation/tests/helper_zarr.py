from typing import Dict

import allure
import numpy as np
import pytest
from fixtures.data import BINNING_FACTORS

ZATTRS_AXIS_ORDER = ["z", "y", "x"]
SPACING_TOLERANCE = 0.001


class HelperTestZarrHeader:
    """
    This is a helper class that contains pytests for checking the header of a zarr file.
    See helper_mrc.py for more information (quite similar).
    """

    # Class variables that need to be set by the subclass
    zarr_headers: Dict[str, Dict[str, Dict]] = None
    skip_z_axis_checks: bool = False
    spacing: float = None
    permitted_zarr_datatypes: list = [np.int8, np.float32]

    ### BEGIN ZARR Self-consistency tests ###
    def zarr_header_helper(
        self,
        check_func: callable,
        **kwargs,
    ):
        """Helper function to check the header of the zarr file."""
        for zarr_filename, header_data in self.zarr_headers.items():
            print(f"Checking {zarr_filename}")
            check_func(header_data, zarr_filename, **kwargs)

    @allure.title("Zarr: zattrs path metadata is correct")
    def test_zattrs_path(self):
        def check_zattrs_path(header_data, _zarr_filename):
            del _zarr_filename
            for binning_factor in BINNING_FACTORS:  # 1x, 2x, 4x
                assert header_data["zattrs"]["multiscales"][0]["datasets"][binning_factor]["path"] == str(
                    binning_factor,
                )

        self.zarr_header_helper(check_zattrs_path)

    @allure.title("Zarr: zattrs axes order is correct")
    def test_zattrs_axes(self):
        def check_zattrs_axes(header_data, _zaar_filename):
            del _zaar_filename
            assert len(header_data["zattrs"]["multiscales"][0]["axes"]) == 3
            for i, axis in enumerate(ZATTRS_AXIS_ORDER):
                assert header_data["zattrs"]["multiscales"][0]["axes"][i] == {
                    "name": axis,
                    "type": "space",
                    "unit": "angstrom",
                }

        self.zarr_header_helper(check_zattrs_axes)

    @allure.title("Zarr: zarray data type is correct")
    def test_zarray_datatype(self):
        def check_zarray(header_data, _zarr_filename):
            del _zarr_filename
            zarrays = header_data["zarrays"]
            assert len(zarrays) == 3
            for zarray in zarrays.values():
                assert np.dtype(zarray["dtype"]) in self.permitted_zarr_datatypes

        self.zarr_header_helper(check_zarray)

    ### END ZARR Self-consistency tests ###

    ### BEGIN Voxel-spacing tests ###
    @allure.title("Zarr: zattrs voxel spacings are correct")
    def test_zattrs_voxel_spacings(self):
        def check_zattrs_voxel_spacings(header_data, _zarr_filename):
            del _zarr_filename
            for binning_factor in BINNING_FACTORS:  # 1x, 2x, 4x
                datasets_entry = header_data["zattrs"]["multiscales"][0]["datasets"][binning_factor]
                axes = [1, 2] if self.skip_z_axis_checks else [0, 1, 2]  # z, y, x
                for axis in axes:
                    assert datasets_entry["coordinateTransformations"][0]["scale"][axis] == pytest.approx(
                        self.spacing * 2**binning_factor,
                        abs=SPACING_TOLERANCE * 2**binning_factor,
                    )

        self.zarr_header_helper(check_zattrs_voxel_spacings)

    ### END Voxel-spacing tests ###
