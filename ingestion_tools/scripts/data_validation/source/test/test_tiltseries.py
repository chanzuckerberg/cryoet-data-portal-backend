import allure
import pytest
from importers.tiltseries import TiltSeriesImporter
from pyarrow._fs import FileSystem

from data_validation.shared.helper.helper_mrc_zarr import HelperTestMRCZarrHeader
from data_validation.shared.util import get_file_type, get_mrc_header, get_zarr_metadata


@pytest.mark.tiltseries
@pytest.mark.parametrize(
    "tiltseries",
    pytest.cryoet.tiltseries,
    ids=[f"{ts.get_run().name}-{ts.identifier}" for ts in pytest.cryoet.tiltseries],
    scope="session",
)
class TestTiltSeries(HelperTestMRCZarrHeader):

    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_zarr_header_class_variables(
            self,
            tiltseries: list[TiltSeriesImporter],
            filesystem: FileSystem,
    ):
        self.spacegroup = 0  # 2D image
        self.file_type = get_file_type(tiltseries.name)
        file_path = tiltseries.volume_filename

        if tiltseries.allow_imports:
            if self.file_type == "mrc":
                self.mrc_headers = {file_path: get_mrc_header(file_path, filesystem, fail_test=False)}
            elif self.file_type == "zarr":
                self.zarr_headers = get_zarr_metadata(file_path, filesystem, fail_test=False)
        self.spacing = tiltseries.get_base_metadata().get("pixel_spacing")
        self.skip_z_axis_checks = True

    @allure.title("Tiltseries: sanity check filetype.")
    def test_file_type(self):
        assert self.file_type != "unknown"

    @allure.title("Zarr and MRC: files exist for each entity.")
    def test_zarr_mrc_both_exist(self):
        pytest.skip("Both formats won't exist for source data")

    @allure.title("Zarr and MRC: headers are consistent.")
    def test_zarr_mrc_volume_size(self):
        pytest.skip("Both formats won't exist for source data")
