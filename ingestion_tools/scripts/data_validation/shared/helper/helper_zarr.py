from typing import Dict

import allure
import numpy as np
import pytest

from common.cryoet_profile import check_profile

ZATTRS_AXIS_ORDER = ["z", "y", "x"]
LEADING_AXES = [{"name": "t", "type": "time", "unit": "second"}, {"name": "c", "type": "channel"}]
SPACING_TOLERANCE = 0.001
MIN_LEVELS = 3


class HelperTestZarrHeader:
    """
    This is a helper class that contains pytests for checking the header of a zarr file (Zarr v3 / OME-NGFF 0.5;
    ``zattrs`` holds the OME metadata, ``zarrays`` the zarr.json of each level, see util.get_zarr_metadata).
    See helper_mrc.py for more information (quite similar).
    """

    # Class variables that need to be set by the subclass
    zarr_headers: Dict[str, Dict[str, Dict]] = None
    skip_z_axis_checks: bool = False
    spacing: float = None
    permitted_zarr_datatypes: list = [np.int8, np.int16, np.float32, np.float64]
    error_on_no_zarr_header: bool = True

    ### BEGIN ZARR Self-consistency tests ###
    def zarr_header_helper(
        self,
        check_func: callable,
        **kwargs,
    ):
        """Helper function to check the header of the zarr file."""
        if not self.zarr_headers:
            if self.error_on_no_zarr_header:
                pytest.fail("No zarr headers available")
            else:
                pytest.skip("No zarr headers to check")

        for zarr_filename, header_data in self.zarr_headers.items():
            print(f"Checking {zarr_filename}")
            check_func(header_data, zarr_filename, **kwargs)

    @allure.title("Zarr: zattrs path metadata is correct")
    def test_zattrs_path(self):
        def check_zattrs_path(header_data, _zarr_filename):
            del _zarr_filename
            datasets = header_data["zattrs"]["multiscales"][0]["datasets"]
            assert len(datasets) >= MIN_LEVELS, f"Expected at least {MIN_LEVELS} levels, found {len(datasets)}"
            for level, dataset in enumerate(datasets):  # 1x, 2x, 4x, ...
                assert dataset["path"] == str(level), f"Path metadata is incorrect for level {level}"
            assert sorted(header_data["zarrays"]) == list(range(len(datasets))), "Levels and arrays do not match"

        self.zarr_header_helper(check_zattrs_path)

    @allure.title("Zarr: zattrs axes order is correct")
    def test_zattrs_axes(self):
        def check_zattrs_axes(header_data, _zaar_filename):
            del _zaar_filename
            axes = header_data["zattrs"]["multiscales"][0]["axes"]
            assert len(axes) in (3, 5), "Incorrect number of axes"
            if len(axes) == 5:  # cryoET-profile volumes: [t, c, z, y, x]
                assert axes[:2] == LEADING_AXES, f"Leading axes {axes[:2]} are incorrect"
            for i, axis in enumerate(ZATTRS_AXIS_ORDER):
                assert axes[len(axes) - 3 + i] == {
                    "name": axis,
                    "type": "space",
                    "unit": "angstrom",
                }, f"Axis {axis} is incorrect"

        self.zarr_header_helper(check_zattrs_axes)

    @allure.title("Zarr: zarray data type is correct")
    def test_zarray_datatype(self):
        def check_zarray(header_data, _zarr_filename):
            del _zarr_filename
            zarrays = header_data["zarrays"]
            assert len(zarrays) >= MIN_LEVELS, "Incorrect number of zarrays"
            for zarray in zarrays.values():
                assert zarray.get("zarr_format") == 3, "Not a Zarr v3 array"
                assert (
                    np.dtype(zarray["data_type"]) in self.permitted_zarr_datatypes
                ), f"Data type is {zarray['data_type']} is not permitted"

        self.zarr_header_helper(check_zarray)

    @allure.title("Zarr: tomograms and tilt series follow the cryoET storage profile")
    @allure.description(
        "Images with a dca block (tomograms, tilt series) must meet every MUST rule of the cryoET storage profile "
        "v0.1: layout, levels, transforms, codecs, encoding attributes and image statistics.",
    )
    def test_cryoet_profile(self):
        def check(header_data, zarr_filename):
            if header_data.get("image_type") is None:
                pytest.skip(f"{zarr_filename} is not a cryoET-profile image")
            arrays = {str(k): v for k, v in header_data["zarrays"].items()}
            errors = check_profile(header_data["group"], arrays)
            assert not errors, f"{zarr_filename}: " + "; ".join(errors)

        self.zarr_header_helper(check)

    ### END ZARR Self-consistency tests ###

    ### BEGIN Voxel-spacing tests ###
    @allure.title("Zarr: zattrs voxel spacings are correct")
    def test_zattrs_voxel_spacings(self):
        def check_zattrs_voxel_spacings(header_data, _zarr_filename):
            del _zarr_filename
            datasets = header_data["zattrs"]["multiscales"][0]["datasets"]
            for level, datasets_entry in enumerate(datasets):  # 1x, 2x, 4x, ...
                scale = datasets_entry["coordinateTransformations"][0]["scale"][-3:]  # z, y, x
                axes = [1, 2] if self.skip_z_axis_checks else [0, 1, 2]
                for axis in axes:
                    assert scale[axis] == pytest.approx(
                        self.spacing * 2**level,
                        abs=SPACING_TOLERANCE * 2**level,
                    ), f"Voxel spacing is incorrect for axis {axis} and level {level}"

        self.zarr_header_helper(check_zattrs_voxel_spacings)

    ### END Voxel-spacing tests ###
