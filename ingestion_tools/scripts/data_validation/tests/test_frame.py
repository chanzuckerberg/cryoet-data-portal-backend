import os
import warnings
from typing import Dict, List, Union

import allure
import pandas as pd
import pytest
import tifffile
from mrcfile.mrcinterpreter import MrcInterpreter
from tests.helper_mrc import HelperTestMRCHeader, mrc_allure_title

PERMITTED_FRAME_EXTENSIONS = [".mrc", ".tif", ".tiff", ".eer", ".mrc.bz2"]


@pytest.mark.frame
@pytest.mark.parametrize("run_name", pytest.run_name, scope="session")
class TestFrame(HelperTestMRCHeader):
    @pytest.fixture(autouse=True)
    def set_helper_test_mrc_header_class_variables(
        self,
        frames_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]],
    ):
        self.spacegroup = 0  # 2D image
        self.mrc_headers = {k: v for k, v in frames_headers.items() if isinstance(v, MrcInterpreter)}

    ### DON'T RUN SOME MRC HEADER TESTS ###
    @mrc_allure_title
    def test_nlabel(self):
        pytest.skip("Not applicable for frame files")

    @mrc_allure_title
    def test_nversion(self):
        pytest.skip("Not applicable for frame files")

    @mrc_allure_title
    def test_datatype(self):
        pytest.skip("Not applicable for frame files")

    @mrc_allure_title
    def test_mrc_spacing(self):
        pytest.skip("Not applicable for frame files")

    ### BEGIN Self-consistency tests ###
    @allure.title("Frames: valid extensions.")
    def test_extensions(self, frames_files: List[str]):
        errors = []

        for frame_file in frames_files:
            if not any(frame_file.endswith(ext) for ext in PERMITTED_FRAME_EXTENSIONS):
                errors.append(f"Invalid frame file extension: {frame_file}")

        assert not errors, "\n".join(errors)

    @allure.title("Frames: consistent dimensions and pixel spacings (MRC & TIFF).")
    def test_consistent(self, frames_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]]):
        return helper_tiff_mrc_consistent(frames_headers)

    ### END Self-consistency tests ###

    ### BEGIN Tiltseries consistency tests ###
    @allure.title("Frames: number of subframes in mdoc matches the number of subframes in the frame file.")
    def test_mdoc_numsubframes(
        self,
        frames_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]],
        tiltseries_mdoc: pd.DataFrame,
    ):
        errors = []
        for _, row in tiltseries_mdoc.iterrows():
            frame_file = os.path.basename(str(row["SubFramePath"]).replace("\\", "/"))
            if frame_file not in frames_headers:
                # Frame file does not exist, this will get caught by a test_tilt_angles test
                continue

            header_entity = frames_headers[frame_file]
            if isinstance(header_entity, list) and isinstance(header_entity[0], tifffile.TiffPage):
                if len(header_entity) != row["NumSubFrames"]:
                    errors.append(
                        f"Number of subframes do not match: {len(header_entity)} != {row['NumSubFrames']}, {frame_file}",
                    )
            elif isinstance(header_entity, MrcInterpreter):
                if header_entity.header.nz != row["NumSubFrames"]:
                    errors.append(
                        f"Number of subframes do not match: {header_entity.header.nz} != {row['NumSubFrames']}, {frame_file}",
                    )
            else:
                warnings.warn(f"Unsupported frame type: {type(frame_file)}, {frame_file}", stacklevel=2)

        assert not errors, "\n".join(errors)

    @allure.title("Frames: tiltseries pixel spacing is an integer multiple of the frame pixel spacing.")
    def test_tiltseries_pixel_spacing(
        self,
        frames_headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]],
        tiltseries_metadata: Dict,
    ):
        for frame_file, frame_header in frames_headers.items():
            if isinstance(frame_header, MrcInterpreter):
                # only need to check the first frame, since we check that all frames have the same pixel spacing
                assert tiltseries_metadata["pixel_spacing"] / frame_header.voxel_size["x"] == pytest.approx(
                    round(tiltseries_metadata["pixel_spacing"] / frame_header.voxel_size["x"]),
                    abs=0.001,
                ), f"Pixel spacing does not match tiltseries metadata, {frame_file}"
                return

    ### END Tiltseries consistency tests ###


### Helper functions (used in other test classes) ###
def helper_tiff_mrc_consistent(headers: Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]]):
    """Check that the dimensions (MRC & TIFF) and pixel spacings (MRC) between MRC and/or TIFF files are consistent."""
    errors = []
    dimensions = None
    pixel_spacing = None

    for filename, header_entity in headers.items():
        if isinstance(header_entity, list) and isinstance(header_entity[0], tifffile.TiffPage):
            curr_dimensions = header_entity[0].shape
            if not all(page.shape == curr_dimensions for page in header_entity):
                errors.append(f"Not all pages have the same dimensions {filename}")

            if dimensions is None:
                dimensions = curr_dimensions
            elif curr_dimensions != dimensions:
                errors.append(
                    f"Dimensions do not match: {curr_dimensions} != {dimensions}, {filename}",
                )
        elif isinstance(header_entity, MrcInterpreter):
            header = header_entity.header
            if dimensions is None:
                dimensions = (header.nx, header.ny)
            elif (header.nx, header.ny) != dimensions:
                errors.append(
                    f"Dimensions do not match: ({header.nx}, {header.ny}) != {dimensions}, {filename}",
                )
            if pixel_spacing is None:
                pixel_spacing = header_entity.voxel_size["x"]
            elif abs(header_entity.voxel_size["x"] - pixel_spacing) > 0.001:
                errors.append(
                    f"Pixel spacing do not match: {header_entity.voxel_size['x']} != {pixel_spacing}, {filename}",
                )

            if abs(header_entity.voxel_size["x"] - header_entity.voxel_size["y"]) > 0.001:
                errors.append(f"Y and X pixel spacings do not match: {header_entity.voxel_size}, {filename}")
        else:
            warnings.warn(f"Unsupported type: {type(header)}, {filename}", stacklevel=2)

    assert not errors, "\n".join(errors)
