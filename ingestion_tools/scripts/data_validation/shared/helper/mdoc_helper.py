import os
import warnings

import allure
import pandas as pd
import tifffile
from mrcfile.mrcinterpreter import MrcInterpreter


class MdocTestHelper:

    ### BEGIN MDOC tests ###
    @allure.title("Mdoc: tilt angles are within the expected range [-90, 90].")
    def test_frames_mdoc_range(self, mdoc_data: pd.DataFrame):
        assert mdoc_data["TiltAngle"].min() >= -90
        assert mdoc_data["TiltAngle"].max() <= 90

    @allure.title("Mdoc: number of mdoc sections equal number of frames files.")
    def test_mdoc_frames(self, mdoc_data: pd.DataFrame, frames_files: list[str]):
        assert len(mdoc_data) == len(frames_files)

    @allure.title("Mdoc: Every mdoc SubFramePath filename matches a frames file (one-to-one).")
    def test_mdoc_frame_paths(
            self, frames_files: list[str], mdoc_data: pd.DataFrame,
    ):
        standardize_frames_files = [os.path.basename(f) for f in frames_files]
        standardized_mdoc_entries = [
            os.path.basename(str(row["SubFramePath"]).replace("\\", "/"))
            for _, row in mdoc_data.iterrows()
        ]

        mdoc_with_missing_frames = [
            entry for entry in standardized_mdoc_entries if entry not in standardize_frames_files
        ]
        frames_with_missing_mdoc = [
            entry for entry in standardize_frames_files if entry not in standardized_mdoc_entries
        ]

        errors = []
        if len(standardize_frames_files) != len(standardized_mdoc_entries):
            errors.append(
                f"# of mdoc entries ({len(standardized_mdoc_entries)}) != # of frames files ({len(standardize_frames_files)})",
            )
        if mdoc_with_missing_frames:
            errors.append(f"mdoc entries do not have frames files: {mdoc_with_missing_frames}")
        if frames_with_missing_mdoc:
            errors.append(f"Frames files do not have mdoc entries: {frames_with_missing_mdoc}")

        assert len(errors) == 0, "\n".join(errors)

    @allure.title("Mdoc: number of subframes in mdoc matches the number of subframes in the frame file.")
    def test_mdoc_numsubframes(
            self,
            frames_headers: dict[str, list[tifffile.TiffPage | MrcInterpreter]],
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
