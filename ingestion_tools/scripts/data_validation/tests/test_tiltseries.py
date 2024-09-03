import math
import os
from typing import Dict

import pytest
from data_validation.tests.helper_mrc_zarr import HelperTestMRCZarrHeader
from data_validation.tests.test_deposition import HelperTestDeposition
from fixtures.data import BINNING_FACTORS
from mrcfile.mrcinterpreter import MrcInterpreter


# By setting this scope to session, scope="session" fixtures will be reinitialized for each run + voxel_spacing combination
@pytest.mark.tiltseries
@pytest.mark.parametrize("run_name", pytest.run_name, scope="session")
class TestTiltseries(HelperTestMRCZarrHeader):

    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_zarr_header_class_variables(
        self,
        tiltseries_mrc_header: Dict[str, MrcInterpreter],
        tiltseries_zarr_header: Dict[str, Dict[str, Dict]],
        tiltseries_metadata: Dict,
    ):
        self.spacegroup = 0  # 2D image
        self.mrc_headers = tiltseries_mrc_header
        self.zarr_headers = tiltseries_zarr_header
        self.spacing = tiltseries_metadata["pixel_spacing"]
        self.skip_z_axis_checks = True

    def test_mrc_mode(self):
        pytest.skip("Not applicable for tiltseries files")

    ### BEGIN metadata self-consistency tests ###
    def test_tiltseries_metadata(self, tiltseries_metadata: Dict, run_name: str):
        """A tiltseries metadata sanity check."""
        assert tiltseries_metadata["acceleration_voltage"] > 0
        assert tiltseries_metadata["spherical_aberration_constant"] > 0
        assert tiltseries_metadata["tilting_scheme"]
        assert tiltseries_metadata["total_flux"] > 0
        assert tiltseries_metadata["run_name"] == run_name

    def test_tiltseries_deposition(self, tiltseries_metadata: Dict, bucket, filesystem):
        HelperTestDeposition.check_deposition_metadata(tiltseries_metadata["deposition_id"], bucket, filesystem)

    def test_tiltseries_size_scales(self, tiltseries_metadata: Dict):
        """Check that the tiltseries size is equal to first scale entry (0 binning factor)."""
        assert tiltseries_metadata["size"] == tiltseries_metadata["scales"][0]

    def test_tiltseries_scales(self, tiltseries_metadata: Dict):
        """Check that the tiltseries scales data is consistent."""
        # z size is not scaled, stays consistent
        assert len({scale["z"] for scale in tiltseries_metadata["scales"]}) == 1

        curr_scale = tiltseries_metadata["scales"][0]
        for scale in tiltseries_metadata["scales"][1:]:
            assert math.ceil(curr_scale["y"] / 2) == scale["y"]
            assert math.ceil(curr_scale["x"] / 2) == scale["x"]
            curr_scale = scale

    ### END metadata self-consistency tests ###

    ### BEGIN metadata-MRC/Zarr consistency tests ###
    def test_tiltseries_size_in_mrc(self, tiltseries_metadata: Dict):
        """Check that the tiltseries volume size matches the MRC header volume size."""

        def check_size_in_mrc(header, _interpreter, _mrc_filename, tiltseries_metadata):
            del _interpreter, _mrc_filename
            assert header.nx == tiltseries_metadata["size"]["x"]
            assert header.ny == tiltseries_metadata["size"]["y"]
            assert header.nz == tiltseries_metadata["size"]["z"]

        self.mrc_header_helper(check_size_in_mrc, tiltseries_metadata=tiltseries_metadata)

    def test_tiltseries_scales_in_zarr(self, tiltseries_metadata: Dict):
        """Check that the tiltseries binning factor scales matches the Zarr header volume size."""

        def check_size_in_zarr(header_data, _zarr_filename, tiltseries_metadata):
            del _zarr_filename
            for binning_factor in BINNING_FACTORS:  # Check all binning factors
                assert header_data["zarrays"][binning_factor]["shape"] == [
                    tiltseries_metadata["scales"][binning_factor]["z"],
                    tiltseries_metadata["scales"][binning_factor]["y"],
                    tiltseries_metadata["scales"][binning_factor]["x"],
                ]

        self.zarr_header_helper(check_size_in_zarr, tiltseries_metadata=tiltseries_metadata)

    def test_tiltseries_zarr_matches(
        self,
        tiltseries_metadata: Dict,
        tiltseries_zarr_header: Dict[str, Dict[str, Dict]],
    ):
        """Check that the metadata-listed zarr file matches the actual file."""
        assert len(tiltseries_zarr_header) == 1
        assert tiltseries_metadata["omezarr_dir"] == os.path.basename(list(tiltseries_zarr_header.keys())[0])

    def test_tiltseries_mrc_matches(
        self,
        tiltseries_metadata: Dict,
        tiltseries_mrc_header: Dict[str, MrcInterpreter],
    ):
        """Check that the metadata-listed mrc file matches the actual file."""
        assert len(tiltseries_metadata["mrc_files"]) == 1
        assert len(tiltseries_mrc_header) == 1
        assert tiltseries_metadata["mrc_files"][0] == os.path.basename(list(tiltseries_mrc_header.keys())[0])

    ### END metadata-MRC/Zarr consistency tests ###
