import math

import allure
import pytest
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

    # The MRC files expected next to the zarr files. None: one per zarr (same name). Images ingested with --skip-mrc
    # have no MRC; for them, the test classes derive this from the metadata (which then records no MRC).
    expected_mrc_files: set[str] | None = None

    ### BEGIN Cross-format consistency tests ###
    @allure.title("Zarr and MRC: files exist for each entity.")
    def test_zarr_mrc_both_exist(self):
        zarr_files = set(self.zarr_headers.keys())
        mrc_files = set(self.mrc_headers.keys())
        expected = self.expected_mrc_files
        if expected is None:
            expected = {f.replace(".zarr", ".mrc") for f in zarr_files}
        if not expected and not mrc_files:
            pytest.skip("No MRC files (OME-Zarr only, ingested with --skip-mrc)")
        assert expected <= {f.replace(".zarr", ".mrc") for f in zarr_files}, "MRC files without a zarr"
        assert mrc_files == expected

    @allure.title("Zarr and MRC: headers are consistent.")
    @allure.description(
        "Zarray shape (volume size) should match the MRC volume size, re-scaled to account for binning.",
    )
    def test_zarr_mrc_volume_size(self):
        if not self.mrc_headers and not self.error_on_no_mrc_header:
            pytest.skip("No MRC files (OME-Zarr only, ingested with --skip-mrc)")

        def check_volume_size(header_data, zarr_filename):
            mrc_file = zarr_filename.replace(".zarr", ".mrc")
            if mrc_file not in self.mrc_headers:
                # no MRC for this image (--skip-mrc); test_zarr_mrc_both_exist checks which MRC files must exist
                return
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
