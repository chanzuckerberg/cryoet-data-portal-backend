import math

import allure
from data_validation.tests.helper_mrc import HelperTestMRCHeader
from data_validation.tests.helper_zarr import HelperTestZarrHeader


class HelperTestMRCZarrHeader(HelperTestMRCHeader, HelperTestZarrHeader):
    """
    Helper class to validate MRC and Zarr headers (cross-format checks), as well as individual MRC and Zarr headers.
    See helper_mrc.py and helper_zarr.py for more information.
    """

    ### BEGIN Cross-format consistency tests ###
    @allure.title("Zarr and MRC: files exist for each entity.")
    def test_zarr_mrc_both_exist(self):
        zarr_files = set(self.zarr_headers.keys())
        mrc_files = set(self.mrc_headers.keys())
        assert {f.replace(".zarr", ".mrc") for f in zarr_files} == mrc_files

    @allure.title("Zarr and MRC: headers are consistent.")
    @allure.description(
        "Zarray shape (volume size) should match the MRC volume size, re-scaled to account for binning.",
    )
    def test_zarr_mrc_volume_size(self):
        def check_volume_size(header_data, zarr_filename):
            mrc_file = zarr_filename.replace(".zarr", ".mrc")
            header = self.mrc_headers[mrc_file].header

            zarrays = header_data["zarrays"]
            for i, zarray in zarrays.items():
                zarr_shape = zarray["shape"].copy()
                if self.skip_z_axis_checks:
                    zarr_shape[0] = "N/A"
                binned_header_shape = [
                    "N/A" if self.skip_z_axis_checks else math.ceil(header.nz / 2 ** int(i)),
                    math.ceil(header.ny / 2 ** int(i)),
                    math.ceil(header.nx / 2 ** int(i)),
                ]
                assert (
                    zarr_shape == binned_header_shape
                ), f"zarr shape: {zarr_shape}, binned mrc shape: {binned_header_shape}, binning factor: {i}"

        self.zarr_header_helper(check_volume_size)

    ### END Cross-format consistency tests ###
