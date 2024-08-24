import math

from tests.helper_mrc import HelperTestMRCHeader
from tests.helper_zarr import HelperTestZarrHeader


class HelperTestMRCZarrHeader(HelperTestMRCHeader, HelperTestZarrHeader):
    """
    Helper class to validate MRC and Zarr headers (cross-format checks), as well as individual MRC and Zarr headers.
    See helper_mrc.py and helper_zarr.py for more information.
    """

    ### BEGIN Cross-format consistency tests ###
    def test_zarr_mrc_both_exist(self):
        """Check that both the zarr and mrc annotation files exist for each annotation file."""
        zarr_files = set(self.zarr_headers.keys())
        mrc_files = set(self.mrc_headers.keys())
        assert {f.replace(".zarr", ".mrc") for f in zarr_files} == mrc_files

    def test_zarr_mrc_volume_size(self):
        """Check that the zarray shape (volume size) matches the mrc volume size, for each zarr binning."""

        def check_volume_size(header_data, zarr_filename):
            mrc_file = zarr_filename.replace(".zarr", ".mrc")

            zarrays = header_data["zarrays"]
            for i, zarray in zarrays.items():
                header = self.mrc_headers[mrc_file].header
                binned_header_shape = [
                    math.ceil(header.nz / 2 ** int(i)),
                    math.ceil(header.ny / 2 ** int(i)),
                    math.ceil(header.nx / 2 ** int(i)),
                ]
                assert (
                    zarray["shape"] == binned_header_shape
                ), f"zarr shape: {zarray['shape']}, mrc shape: {[header.nz, header.ny, header.nx]}, binning factor: {i}"

        self.zarr_header_helper(check_volume_size)

    ### END Cross-format consistency tests ###
