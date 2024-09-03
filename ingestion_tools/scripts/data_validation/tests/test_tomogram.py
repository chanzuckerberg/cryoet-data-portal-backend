import math
import os
from typing import Dict

import allure
import pytest
from data_validation.tests.helper_images import check_photo_valid
from data_validation.tests.helper_metadata import basic_metadata_check
from data_validation.tests.helper_mrc import mrc_allure_title
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
@pytest.mark.parametrize("dataset, run_name, voxel_spacing", pytest.dataset_run_spacing_combinations, scope="session")
class TestTomogram(HelperTestMRCZarrHeader):
    def test_tomogram_metadata(self, canonical_tomogram_metadata: Dict):
        """A tomogram metadata sanity check."""
        assert canonical_tomogram_metadata["deposition_id"]
        assert isinstance(canonical_tomogram_metadata["authors"], list)
        assert all(isinstance(authors, dict) for authors in canonical_tomogram_metadata["authors"])

    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_zarr_header_class_variables(
        self,
        tomo_mrc_header: Dict[str, MrcInterpreter],
        tomo_zarr_header: Dict[str, Dict[str, Dict]],
        voxel_spacing: str,
    ):
        self.spacegroup = 1  # single 3D volume
        self.mrc_headers = tomo_mrc_header
        self.zarr_headers = tomo_zarr_header
        self.spacing = float(voxel_spacing)

    ### DON'T RUN SOME MRC HEADER TESTS ###
    @mrc_allure_title
    def test_datatype(self):
        pytest.skip("Not applicable for tomogram files")

    @allure.title("Tomogram: sanity check tomogram metadata.")
    def test_metadata(self, tomogram_metadata: Dict):
        basic_metadata_check(tomogram_metadata)

    @allure.title("Tomogram: metadata has valid key photos.")
    # The key_photo attribute is where the key_images data is stored and can be validated
    def test_key_photos(self, tomogram_metadata: Dict, bucket: str, filesystem: FileSystemApi):
        check_photo_valid(
            tomogram_metadata["key_photo"]["thumbnail"],
            bucket,
            filesystem,
            MIN_THUMBNAIL_WIDTH,
            PHOTO_ASPECT_RATIO,
        )
        check_photo_valid(
            tomogram_metadata["key_photo"]["snapshot"],
            bucket,
            filesystem,
            MIN_SNAPSHOT_WIDTH,
            PHOTO_ASPECT_RATIO,
        )

    @allure.title("Tomogram: valid corresponding deposition metadata.")
    def test_deposition_id(self, tomogram_metadata: Dict, bucket: str, filesystem: FileSystemApi):
        HelperTestDeposition.check_deposition_metadata(tomogram_metadata["deposition_id"], bucket, filesystem)

    @allure.title("Tomogram: metadata size is consistent with scales.")
    def test_size_scales(self, tomogram_metadata: Dict):
        assert tomogram_metadata["size"] == tomogram_metadata["scales"][0]

    @allure.title("Tomogram: metadata scales is self-consistent.")
    def test_scales(self, tomogram_metadata: Dict):
        curr_scale = tomogram_metadata["scales"][0]
        for scale in tomogram_metadata["scales"][1:]:
            assert math.ceil(curr_scale["z"] / 2) == scale["z"]
            assert math.ceil(curr_scale["y"] / 2) == scale["y"]
            assert math.ceil(curr_scale["x"] / 2) == scale["x"]
            curr_scale = scale

    @allure.title("Tomogram: metadata volume size is consistent with MRC header.")
    def test_size_mrc(self, tomogram_metadata: Dict):
        def check_size_mrc(header, _interpreter, _mrc_filename, tomogram_metadata):
            del _interpreter, _mrc_filename
            assert header.nx == tomogram_metadata["size"]["x"]
            assert header.ny == tomogram_metadata["size"]["y"]
            assert header.nz == tomogram_metadata["size"]["z"]

        self.mrc_header_helper(check_size_mrc, tomogram_metadata=tomogram_metadata)

    @allure.title("Tomogram: metadata voxel spacing matches run voxel spacing.")
    def test_voxel_spacing(self, tomogram_metadata: Dict):
        assert tomogram_metadata["voxel_spacing"] == self.spacing

    @allure.title("Tomogram: metadata zarr file matches the actual file.")
    def test_zarr_matches(
        self,
        tomogram_metadata: Dict,
        tomo_zarr_header: Dict[str, Dict[str, Dict]],
    ):
        assert len(tomo_zarr_header) == 1
        assert tomogram_metadata["omezarr_dir"] == os.path.basename(
            list(tomo_zarr_header.keys())[0],
        )

    @allure.title("Tomogram: metadata mrc file matches the actual file.")
    def test_mrc_matches(
        self,
        tomogram_metadata: Dict,
        tomo_mrc_header: Dict[str, MrcInterpreter],
    ):
        assert len(tomogram_metadata["mrc_files"]) == 1
        assert len(tomo_mrc_header) == 1
        assert tomogram_metadata["mrc_files"][0] == os.path.basename(
            list(tomo_mrc_header.keys())[0],
        )
