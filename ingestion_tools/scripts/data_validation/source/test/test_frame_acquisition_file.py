import os
import warnings

import allure
import pandas as pd
import pytest
import tifffile
from mrcfile.mrcinterpreter import MrcInterpreter

from data_validation.shared.helper.mdoc_helper import MdocTestHelper


@pytest.mark.mdoc
@pytest.mark.parametrize("run", pytest.cryoet.runs, ids=[ts.name for ts in pytest.cryoet.runs], scope="session")
class TestFrameAcquisitionFile(MdocTestHelper):

    @allure.title("Mdoc file exists when frames or tiltseries are present")
    def test_mdoc_file_count(self, mdoc_file: str, frames_files: list[str], tiltseries_files: list[str]):
        if frames_files or tiltseries_files:
            assert mdoc_file  is not None

    def test_frames_mdoc_range(self, mdoc_data: pd.DataFrame):
        assert mdoc_data["TiltAngle"].min() >= -90
        assert mdoc_data["TiltAngle"].max() <= 90

    def test_mdoc_frames(self, mdoc_data: pd.DataFrame, frames_files: list[str]):
        assert len(mdoc_data) == len(frames_files)

    def test_mdoc_frame_paths(self, frames_files: list[str], mdoc_data: pd.DataFrame):
        frame_filenames = {os.path.basename(f) for f in frames_files}
        mdoc_entries = {
            os.path.basename(str(row["SubFramePath"]).replace("\\", "/")) for _, row in mdoc_data.iterrows()
        }

        mdoc_with_missing_frames = mdoc_entries - frame_filenames
        frames_with_missing_mdoc = frame_filenames - mdoc_entries

        errors = []
        if len(frame_filenames) != len(mdoc_entries):
            errors.append(
                f"# of mdoc entries ({len(mdoc_entries)}) != # of frames files ({len(frame_filenames)})",
            )
        if mdoc_with_missing_frames:
            errors.append(f"mdoc entries do not have frames files: {mdoc_with_missing_frames}")
        if frames_with_missing_mdoc:
            errors.append(f"Frames files do not have mdoc entries: {frames_with_missing_mdoc}")

        assert len(errors) == 0, "\n".join(errors)

    def test_mdoc_numsubframes(
            self,
            frames_headers: dict[str, list[tifffile.TiffPage] | MrcInterpreter],
            mdoc_data: pd.DataFrame,
    ):
        errors = []
        for _, row in mdoc_data.iterrows():
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

    ### END Self-consistency tests ###
