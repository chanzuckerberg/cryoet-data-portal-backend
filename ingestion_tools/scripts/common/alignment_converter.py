import os.path
from typing import Any

import pandas as pd
from importers.base_importer import BaseImporter

from common.config import DepositionImportConfig


class BaseAlignmentConverter:
    def get_alignment_path(self) -> str | None:
        """
        :return: A str path to the alignment file if exists else None
        """
        return None

    def get_tilt_path(self) -> str | None:
        """
        :return: A str path to the tilt file if exists else None
        """
        return None

    def get_tiltx_path(self) -> str | None:
        """
        :return: A str path to the tiltx file if exists else None
        """
        return None

    def get_per_section_alignment_parameters(self) -> list[dict]:
        """
        Generates the per section alignment parameters from the files
        :return: A list of dictionaries containing the per section alignment parameters
        """
        return []


class IMODAlignmentConverter(BaseAlignmentConverter):
    def __init__(
        self,
        paths: list[str],
        config: DepositionImportConfig,
        parents: dict[str, BaseImporter],
        output_prefix: str,
    ):
        self.paths = paths
        self.config = config
        self.parents = parents
        self.output_prefix = output_prefix

    def get_alignment_path(self) -> str | None:
        return self._get_files_with_suffix([".xf"])

    def get_tilt_path(self) -> str | None:
        return self._get_files_with_suffix([".tlt"])

    def get_tiltx_path(self) -> str | None:
        return self._get_files_with_suffix([".tltx", ".xtilt"])

    def get_per_section_alignment_parameters(self) -> list[dict]:
        tlt_data = self._get_dataframe(self.get_tilt_path(), ["tilt_angle"])
        tltx_data = self._get_dataframe(self.get_tiltx_path(), ["volume_x_rotation"])
        xf_column_names = ["rotation_0", "rotation_1", "rotation_2", "rotation_3", "x_offset", "y_offset"]
        xf_data = self._get_dataframe(self.get_alignment_path(), xf_column_names)

        result = []
        rows = len(xf_data.index)
        for index in range(0, rows):
            item = {
                **self._get_xf_psap(xf_data, index),
                "z_index": index,
                "tilt_angle": None if tlt_data.empty else tlt_data["tilt_angle"][index],
                "volume_x_rotation": 0 if tltx_data.empty else tltx_data["volume_x_rotation"][index],
            }
            result.append(item)
        return result

    def _get_dataframe(self, path: str, names: list[str]) -> pd.DataFrame:
        if not path:
            return pd.DataFrame()
        local_path = self.config.fs.localreadable(path)
        return pd.read_csv(local_path, sep=r"\s+", header=None, names=names)

    def _get_files_with_suffix(self, valid_suffix: list[str]) -> str | None:
        for path in self.paths:
            if path.endswith(tuple(valid_suffix)):
                file_name = os.path.basename(path)
                dest_filepath = os.path.join(self.output_prefix, file_name)
                if self.config.fs.exists(dest_filepath):
                    return dest_filepath
        return None

    @classmethod
    def _get_xf_psap(cls, xf_data: pd.DataFrame, index: int) -> dict:
        if xf_data.empty:
            return {
                "in_plane_rotation": (0, 0, 0, 0),
                "x_offset": 0,
                "y_offset": 0,
            }
        return {
            "in_plane_rotation": (
                xf_data["rotation_0"][index],
                xf_data["rotation_1"][index],
                xf_data["rotation_2"][index],
                xf_data["rotation_3"][index],
            ),
            "x_offset": xf_data["x_offset"][index],
            "y_offset": xf_data["y_offset"][index],
        }


def alignment_converter_factory(
    config: DepositionImportConfig,
    metadata: dict[str, Any],
    paths: list[str],
    parents: dict[str, Any],
    output_prefix: str,
) -> BaseAlignmentConverter:
    alignment_format = metadata.get("format")
    if alignment_format == "IMOD":
        return IMODAlignmentConverter(paths, config, parents, output_prefix)

    return BaseAlignmentConverter()
