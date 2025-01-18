import pytest
from importers.tiltseries import TiltSeriesImporter


@pytest.mark.parametrize("tiltseries", pytest.cryoet.tiltseries, ids=[ts.name for ts in pytest.cryoet.tiltseries], scope="session")
class TestTiltSeries:

    @pytest.fixture(scope="class")
    def pixel_spacing(self, tiltseries: TiltSeriesImporter):
        return tiltseries.get_voxel_size()

    @pytest.fixture(scope="class")
    def tiltseries_file_type(self, tiltseries: TiltSeriesImporter) -> str:
        if tiltseries.name.endswith(".zarr"):
            return "zarr"
        elif any(tiltseries.name.endswith(extension) for extension in [".mrc", ".st"]):
            return "mrc"
        return "unknown"

    def test_tiltseries_file_type(self, tiltseries_file_type: str):
        assert tiltseries_file_type != "unknown"

    def test_tiltseries_pixel_spacing(self, pixel_spacing: float, tiltseries: TiltSeriesImporter):
        assert pytest.approx(pixel_spacing, abs=0.001) == tiltseries.get_pixel_spacing()
