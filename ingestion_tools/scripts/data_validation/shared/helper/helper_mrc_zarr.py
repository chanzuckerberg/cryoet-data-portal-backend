import math

import allure
from data_validation.shared.helper.helper_mrc import HelperTestMRCHeader
from data_validation.shared.helper.helper_zarr import HelperTestZarrHeader

from common.cryoet_profile import fourier_plan


def expected_level_shape(header, level: int, image_type: str | None) -> list[int]:
    """z, y, x size of a level of a volume whose level 0 has the MRC's size: mean binning (and the mask pyramids)
    halve every axis, rounding up; tilt series are Fourier-cropped in y and x only (cryoET profile)."""
    if image_type == "tilt_series":
        if level == 0:
            return [int(header.nz), int(header.ny), int(header.nx)]
        s = 2**level
        return [int(header.nz), fourier_plan(int(header.ny), s).m, fourier_plan(int(header.nx), s).m]
    return [math.ceil(int(n) / 2**level) for n in (header.nz, header.ny, header.nx)]


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
                zarr_shape = list(zarray["shape"][-3:])  # z, y, x (5-D volumes: [1, 1, z, y, x])
                expected = expected_level_shape(header, int(i), header_data.get("image_type"))
                if self.skip_z_axis_checks:
                    zarr_shape[0] = expected[0] = "N/A"
                assert zarr_shape == expected, f"zarr shape: {zarr_shape}, expected from mrc: {expected}, level: {i}"

        self.zarr_header_helper(check_volume_size)

    ### END Cross-format consistency tests ###
