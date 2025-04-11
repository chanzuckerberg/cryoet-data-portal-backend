import os
import warnings

import allure
import pandas as pd
import pytest
import tifffile
from mrcfile.mrcinterpreter import MrcInterpreter


class MdocTestHelper:

    @pytest.fixture
    def mdoc_sub_frame_path(self, mdoc_data: pd.DataFrame) -> list[str]:
        return [
            os.path.basename(str(row["SubFramePath"]).replace("\\", "/"))
            for _, row in mdoc_data.iterrows()
            if "SubFramePath" in row
        ]

    ### BEGIN MDOC tests ###
    @allure.title("Mdoc: tilt angles are within the expected range [-90, 90].")
    def test_frames_mdoc_range(self, mdoc_data: pd.DataFrame):
        assert mdoc_data["TiltAngle"].min() >= -90, "Minimum tilt angle is less than -90"
        assert mdoc_data["TiltAngle"].max() <= 90, "Maximum tilt angle is greater than 90"

    @allure.title("Mdoc:tilt axis angle in mdoc file matches that in tilt series metadata (+/- 10 deg)")
    def test_mdoc_tilt_axis_angle_in_tiltseries(self, mdoc_data: pd.DataFrame, tiltseries_metadata: dict[str, dict]):
        # TODO: see if this is covered by test_tilt_axis_angle
        if tiltseries_metadata["tilt_axis_angle"] is None:
            pytest.skip("Tilt axis angle not found in tilt series metadata")
        assert abs(mdoc_data["TiltAngle"].iloc[0] - tiltseries_metadata["tilt_angle"]) < 10, \
            f"Tilt axis angle in mdoc file {mdoc_data['TiltAxisAngle'].iloc[0]} does not match tilt series metadata {tiltseries_metadata['tilt_axis_angle']}"

    @allure.title("Mdoc: tilt axis angle in mdoc file matches that in the alignment metadata [per_section_alignment_parameters.tilt_angle] (+/- 10 deg)")
    def test_mdoc_tilt_axis_angle_in_alignment_per_section_alignment_parameters(self, mdoc_data: pd.DataFrame, alignment_metadata: dict[str, dict]):
        if not alignment_metadata["per_section_alignment_parameters"]:
            pytest.skip("Alignment metadata missing per_section_alignment_parameters.")
        errors = []
        for i, psap in enumerate(alignment_metadata["per_section_alignment_parameters"]):
            if tilt_angle:=psap.get("tilt_angle") is not None:
                try:
                    assert abs(mdoc_data["TiltAxisAngle"].iloc[0] - tilt_angle) < 10, \
                        f"Tilt axis angle in mdoc file {mdoc_data['TiltAxisAngle'].iloc[0]} does not match alignment metadata['per_section_alignment_parameter'][{i}]['tilt_angle']: {tilt_angle}"
                except AssertionError as e:
                    errors.append(str(e))
        assert not errors, "\n".join(errors)

    @allure.title("Mdoc: number of mdoc sections, equal number of frames files, equals number of items in frames metadata.")
    def test_mdoc_frames(self, mdoc_data: pd.DataFrame, frames_files: list[str], frame_metadata: dict[str, dict]):
        frames_len = len(frames_files)
        if frames_len == 0:
            pytest.skip("No frame files to compare")
        frames_metadata_len = len(frame_metadata["frames"])
        mdoc_len = len(mdoc_data)
        assert mdoc_len == frames_len == frames_metadata_len, f"Number of mdoc sections {mdoc_len} mismatches number of frames: {frames_len} or frames metadata: {frames_metadata_len}"

    @allure.title("Mdoc: Every mdoc filename has an entry for SubFramePath.")
    def test_mdoc_sub_frame_paths(self, mdoc_data: pd.DataFrame):
        for _, row in mdoc_data.iterrows():
            assert "SubFramePath" in row, "SubFramePath not found in mdoc entry"

    @allure.title("Mdoc: Every mdoc SubFramePath filename matches a frames file (one-to-one).")
    def test_mdoc_frame_paths(
        self,
        frames_files: list[str],
        mdoc_data: pd.DataFrame,
    ):
        if len(frames_files) == 0:
            pytest.skip("No frame files to compare")
        errors = []
        standardize_frames_files = [os.path.basename(f) for f in frames_files]
        standardized_mdoc_entries = []
        for _, row in mdoc_data.iterrows():
            if not row.get("SubFramePath"):
                continue
            sub_frame_path = os.path.basename(str(row["SubFramePath"]).replace("\\", "/"))
            standardized_mdoc_entries.append(sub_frame_path)

        mdoc_with_missing_frames = [
            entry for entry in standardized_mdoc_entries if entry not in standardize_frames_files
        ]
        frames_with_missing_mdoc = [
            entry for entry in standardize_frames_files if entry not in standardized_mdoc_entries
        ]

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
            if not row.get("SubFramePath"):
                continue
            frame_file = os.path.basename(str(row["SubFramePath"]).replace("\\", "/"))
            if frame_file not in frames_headers:
                # Frame file does not exist, this will get caught by a test_mdoc_frame_paths test
                continue

            header_entity = frames_headers[frame_file]
            if "NumSubFrames" not in row:
                errors.append("NumSubFrames not found in mdoc file")
            elif isinstance(header_entity, list) and isinstance(header_entity[0], tifffile.TiffPage):
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
