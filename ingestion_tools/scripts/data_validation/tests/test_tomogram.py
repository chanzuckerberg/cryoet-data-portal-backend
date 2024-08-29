import math
import os
from typing import Dict

import allure
import pytest
from mrcfile.mrcinterpreter import MrcInterpreter
from tests.helper_images import check_photo_valid
from tests.helper_metadata import basic_metadata_check
from tests.helper_mrc_zarr import HelperTestMRCZarrHeader
from tests.test_deposition import HelperTestDeposition

from common.fs import FileSystemApi

# values are based on ingestion_tools/scripts/importers/key_image.py
PHOTO_ASPECT_RATIO = 4 / 3
MIN_THUMBNAIL_WIDTH = 100
MIN_SNAPSHOT_WIDTH = 512 * 3 / 4  # account for 4:3 aspect ratio


@pytest.mark.tomogram
@pytest.mark.parametrize("run_name, voxel_spacing", pytest.run_spacing_combinations, scope="session")
class TestTomogram(HelperTestMRCZarrHeader):

    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_zarr_header_class_variables(
        self,
        canonical_tomo_mrc_header: Dict[str, MrcInterpreter],
        canonical_tomo_zarr_header: Dict[str, Dict[str, Dict]],
        voxel_spacing: str,
    ):
        self.spacegroup = 1  # single 3D volume
        self.mrc_headers = canonical_tomo_mrc_header
        self.zarr_headers = canonical_tomo_zarr_header
        self.spacing = float(voxel_spacing)

    @allure.title("Sanity check tomogram metadata.")
    def test_tomogram_metadata(self, canonical_tomogram_metadata: Dict):
        basic_metadata_check(canonical_tomogram_metadata)

    @allure.title("Tomogram metadata has valid key photos.")
    # The key_photo attribute is where the key_images data is stored and can be validated
    def test_tomogram_key_photos(self, canonical_tomogram_metadata: Dict, bucket: str, filesystem: FileSystemApi):
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

    @allure.title("Valid corresponding deposition metadata.")
    def test_tomogram_deposition(self, canonical_tomogram_metadata: Dict, bucket: str, filesystem: FileSystemApi):
        HelperTestDeposition.check_deposition_metadata(canonical_tomogram_metadata["deposition_id"], bucket, filesystem)

    @allure.title("Tomogram metadata size is consistent with scales.")
    def test_tomogram_size_scales(self, canonical_tomogram_metadata: Dict):
        assert canonical_tomogram_metadata["size"] == canonical_tomogram_metadata["scales"][0]

    @allure.title("Tomogram metadata scales is self-consistent.")
    def test_tomogram_scales(self, canonical_tomogram_metadata: Dict):
        curr_scale = canonical_tomogram_metadata["scales"][0]
        for scale in canonical_tomogram_metadata["scales"][1:]:
            assert math.ceil(curr_scale["z"] / 2) == scale["z"]
            assert math.ceil(curr_scale["y"] / 2) == scale["y"]
            assert math.ceil(curr_scale["x"] / 2) == scale["x"]
            curr_scale = scale

    @allure.title("Tomogram metadata volume size is consistent with MRC header.")
    def test_tomogram_size_mrc(self, canonical_tomogram_metadata: Dict):
        def check_size_mrc(header, _interpreter, _mrc_filename, canonical_tomogram_metadata):
            del _interpreter, _mrc_filename
            assert header.nx == canonical_tomogram_metadata["size"]["x"]
            assert header.ny == canonical_tomogram_metadata["size"]["y"]
            assert header.nz == canonical_tomogram_metadata["size"]["z"]

        self.mrc_header_helper(check_size_mrc, canonical_tomogram_metadata=canonical_tomogram_metadata)

    @allure.title("Tomogram metadata voxel spacing matches run voxel spacing.")
    def test_tomogram_voxel_spacing(self, canonical_tomogram_metadata: Dict):
        assert canonical_tomogram_metadata["voxel_spacing"] == self.spacing

    @allure.title("Tomogram metadata zarr file matches the actual file.")
    def test_tomogram_zarr_matches(
        self,
        canonical_tomogram_metadata: Dict,
        canonical_tomo_zarr_header: Dict[str, Dict[str, Dict]],
    ):
        assert len(canonical_tomo_zarr_header) == 1
        assert canonical_tomogram_metadata["omezarr_dir"] == os.path.basename(
            list(canonical_tomo_zarr_header.keys())[0],
        )

    @allure.title("Tomogram metadata mrc file matches the actual file.")
    def test_tomogram_mrc_matches(
        self,
        canonical_tomogram_metadata: Dict,
        canonical_tomo_mrc_header: Dict[str, MrcInterpreter],
    ):
        assert len(canonical_tomogram_metadata["mrc_files"]) == 1
        assert len(canonical_tomo_mrc_header) == 1
        assert canonical_tomogram_metadata["mrc_files"][0] == os.path.basename(
            list(canonical_tomo_mrc_header.keys())[0],
        )
