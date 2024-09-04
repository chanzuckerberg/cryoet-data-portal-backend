"""
key_images testing is also done here (since key_images are part of the tomogram metadata)
"""

import math
import os
from typing import Dict

import pytest
from data_validation.tests.helper_images import check_photo_valid
from data_validation.tests.helper_metadata import basic_metadata_check
from data_validation.tests.helper_mrc_zarr import HelperTestMRCZarrHeader
from data_validation.tests.test_deposition import HelperTestDeposition
from mrcfile.mrcinterpreter import MrcInterpreter

from common.fs import FileSystemApi

# values are based on ingestion_tools/scripts/importers/key_image.py
# (100 pixels is the min width, if it's 4:3 then rotated by key_image.py)
# and frontend aspect ratio (4:3 is used for image display)
PHOTO_ASPECT_RATIO = 4 / 3
MIN_THUMBNAIL_WIDTH = 100
MIN_SNAPSHOT_WIDTH = 512 * 3 / 4  # account for 4:3 aspect ratio


@pytest.mark.tomogram
@pytest.mark.metadata
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestTomogram(HelperTestMRCZarrHeader):

    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_zarr_header_class_variables(
        self,
        canonical_tomo_mrc_header: Dict[str, MrcInterpreter],
        canonical_tomo_zarr_header: Dict[str, Dict[str, Dict]],
        voxel_spacing: float,
    ):
        self.spacegroup = 1  # single 3D volume
        self.mrc_headers = canonical_tomo_mrc_header
        self.zarr_headers = canonical_tomo_zarr_header
        self.spacing = voxel_spacing

    def test_tomogram_metadata(self, canonical_tomogram_metadata: Dict):
        """A tomogram metadata sanity check."""
        basic_metadata_check(canonical_tomogram_metadata)

    # The key_photo attribute is where the key_images data is stored and can be validated
    def test_tomogram_key_photos(self, canonical_tomogram_metadata: Dict, bucket: str, filesystem: FileSystemApi):
        """Check that the key_photos in the metadata are valid."""
        check_photo_valid(
            canonical_tomogram_metadata["key_photo"]["thumbnail"],
            bucket,
            filesystem,
            MIN_THUMBNAIL_WIDTH,
            PHOTO_ASPECT_RATIO,
        )
        check_photo_valid(
            canonical_tomogram_metadata["key_photo"]["snapshot"],
            bucket,
            filesystem,
            MIN_SNAPSHOT_WIDTH,
            PHOTO_ASPECT_RATIO,
        )

    def test_tomogram_deposition(self, canonical_tomogram_metadata: Dict, bucket: str, filesystem: FileSystemApi):
        HelperTestDeposition.check_deposition_metadata(canonical_tomogram_metadata["deposition_id"], bucket, filesystem)

    def test_tomogram_size_scales(self, canonical_tomogram_metadata: Dict):
        """Check that the tomogram size is equal to first scale entry (0 binning factor)."""
        assert canonical_tomogram_metadata["size"] == canonical_tomogram_metadata["scales"][0]

    def test_tomogram_scales(self, canonical_tomogram_metadata: Dict):
        """Check that the tomogram scales data is consistent."""
        curr_scale = canonical_tomogram_metadata["scales"][0]
        for scale in canonical_tomogram_metadata["scales"][1:]:
            assert math.ceil(curr_scale["z"] / 2) == scale["z"]
            assert math.ceil(curr_scale["y"] / 2) == scale["y"]
            assert math.ceil(curr_scale["x"] / 2) == scale["x"]
            curr_scale = scale

    def test_tomogram_size_mrc(self, canonical_tomogram_metadata: Dict):
        """Check that the tomogram volume size matches the metadata size."""

        def check_size_mrc(header, _interpreter, _mrc_filename, canonical_tomogram_metadata):
            del _interpreter, _mrc_filename
            assert header.nx == canonical_tomogram_metadata["size"]["x"]
            assert header.ny == canonical_tomogram_metadata["size"]["y"]
            assert header.nz == canonical_tomogram_metadata["size"]["z"]

        self.mrc_header_helper(check_size_mrc, canonical_tomogram_metadata=canonical_tomogram_metadata)

    def test_tomogram_voxel_spacing(self, canonical_tomogram_metadata: Dict, voxel_spacing: float):
        """Check that the voxel spacing in the metadata matches the voxel spacing used in the run."""
        assert canonical_tomogram_metadata["voxel_spacing"] == voxel_spacing

    def test_tomogram_zarr_matches(
        self,
        canonical_tomogram_metadata: Dict,
        canonical_tomo_zarr_header: Dict[str, Dict[str, Dict]],
    ):
        """Check that the metadata-listed zarr file matches the actual file."""
        assert len(canonical_tomo_zarr_header) == 1
        assert canonical_tomogram_metadata["omezarr_dir"] == os.path.basename(
            list(canonical_tomo_zarr_header.keys())[0],
        )

    def test_tomogram_mrc_matches(
        self,
        canonical_tomogram_metadata: Dict,
        canonical_tomo_mrc_header: Dict[str, MrcInterpreter],
    ):
        """Check that the metadata-listed mrc file matches the actual file."""
        assert len(canonical_tomogram_metadata["mrc_files"]) == 1
        assert len(canonical_tomo_mrc_header) == 1
        assert canonical_tomogram_metadata["mrc_files"][0] == os.path.basename(
            list(canonical_tomo_mrc_header.keys())[0],
        )
