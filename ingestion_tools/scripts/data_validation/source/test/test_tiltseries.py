import allure
import pandas as pd
import pytest
from data_validation.shared.helper.tiltseries_helper import TiltSeriesHelper
from data_validation.shared.util import get_file_type, get_mrc_header, get_zarr_metadata
from importers.base_importer import RunImporter
from importers.tiltseries import TiltSeriesImporter

from common.fs import FileSystemApi
from common.image import get_volume_info


@pytest.mark.tiltseries
@pytest.mark.parametrize(
    "tiltseries",
    pytest.cryoet.tiltseries,
    ids=[f"{ts.get_run().name}-{ts.identifier}" for ts in pytest.cryoet.tiltseries],
    scope="session",
)
class TestTiltSeries(TiltSeriesHelper):

    # This run fixture is required for generating some of the dependencies that are used in testing like raw_tilt_data,
    # mdoc_data, etc.
    @pytest.fixture(scope="session")
    def run(self, tiltseries: TiltSeriesImporter) -> RunImporter:
        return tiltseries.get_run()

    @pytest.fixture
    def tiltseries_metadata(self, tiltseries: TiltSeriesImporter) -> dict:
        return tiltseries.get_base_metadata()

    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_zarr_header_class_variables(
        self,
        tiltseries: TiltSeriesImporter,
        tiltseries_metadata: dict,
        filesystem: FileSystemApi,
    ):
        self.file_type = get_file_type(tiltseries.name)
        file_path = tiltseries.volume_filename

        if tiltseries.allow_imports:
            if self.file_type == "mrc":
                self.mrc_headers = {file_path: get_mrc_header(file_path, filesystem, fail_test=False)}
                self.error_on_no_zarr_header = False
            elif self.file_type == "zarr":
                self.zarr_headers = {file_path: get_zarr_metadata(file_path, filesystem, fail_test=False)}
                self.error_on_no_mrc_header = False
        self.spacing = tiltseries_metadata.get("pixel_spacing")
        self.skip_z_axis_checks = True

    @allure.title("Tiltseries: sanity check filetype.")
    def test_file_type(self):
        assert self.file_type != "unknown", "Tiltseries filetype is unknown"

    @allure.title("Zarr and MRC: files exist for each entity.")
    def test_zarr_mrc_both_exist(self):
        pytest.skip("Both formats won't exist for source data")

    @allure.title("Zarr and MRC: headers are consistent.")
    def test_zarr_mrc_volume_size(self):
        pytest.skip("Both formats won't exist for source data")

    @allure.title("Tiltseries: the number of rawtlt entries should match the number of z-sections")
    def test_z_index_consistency(
        self, tiltseries: TiltSeriesImporter, filesystem: FileSystemApi, raw_tilt_data: pd.DataFrame
    ):
        volume_info = get_volume_info(filesystem, tiltseries.volume_filename)
        assert len(raw_tilt_data) == volume_info.zend - volume_info.zstart, (
            f"Number of rawtlt entries: {len(raw_tilt_data)} != Number of z-sections: "
            f"{volume_info.zend - volume_info.zstart}"
        )
