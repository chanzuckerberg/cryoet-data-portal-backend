from typing import Any

import pandas as pd
from importers.base_importer import BaseImporter

from common.config import DepositionImportConfig


class BaseAlignmentConverter:
    def get_alignment_path(self) -> str | None:
        """Return a str path to the alignment file if exists else None"""
        return None

    def get_tilt_path(self) -> str | None:
        """Return a str path to the tilt file if exists else None"""
        return None

    def get_tiltx_path(self) -> str | None:
        """Return a str path to the tiltx file if exists else None"""
        return None

    def get_per_section_alignment_parameters(self) -> list[dict]:
        """Generates the per section alignment parameters"""
        return []


class IMODAlignmentConverter(BaseAlignmentConverter):
    def __init__(self, path: str, config: DepositionImportConfig, parents: dict[str, BaseImporter]):
        self.path = path
        self.config = config
        self.parents = parents
        self.importers = None

    def get_alignment_path(self) -> str | None:
        importer = self._get_xf_importer()
        return importer.get_dest_filename() if importer else None

    def get_tilt_path(self) -> str | None:
        importer = self._get_tlt_importer()
        return importer.get_dest_filename() if importer else None

    def get_tiltx_path(self) -> str | None:
        importer = self._get_tltx_importer()
        return importer.get_dest_filename() if importer else None

    def get_per_section_alignment_parameters(self) -> list[dict]:
        """Generates the per section alignment parameters"""
        result = []
        tlt_importer = self._get_tlt_importer()
        tltx_importer = self._get_tltx_importer()
        tlt_data = self._get_dataframe(tlt_importer.path if tlt_importer else None, ["tilt_angle"])
        tltx_data = self._get_dataframe(tltx_importer.path if tltx_importer else None, ["volume_x_rotation"])
        xf_data = self._get_xf_data()
        rows = len(xf_data.index)
        for index in range(0, rows):
            item = {
                **self.get_xf_data(xf_data, index),
                "z_index": index,
                "tilt_angle": None if tlt_data.empty else tlt_data["tilt_angle"][index],
                "volume_x_rotation": 0 if tltx_data.empty else tltx_data["volume_x_rotation"][index],
            }
            result.append(item)
        return result

    def _get_xf_data(self) -> pd.DataFrame:
        xf_importer = self._get_xf_importer()
        column_names = ["rotation_0", "rotation_1", "rotation_2", "rotation_3", "x_offset", "y_offset"]
        return self._get_dataframe(xf_importer.path if xf_importer else None, column_names)

    def _get_dataframe(self, path: str, names: list[str]) -> pd.DataFrame:
        if not path:
            return pd.DataFrame()
        local_path = self.config.fs.localreadable(path)
        return pd.read_csv(local_path, sep=r"\s+", header=None, names=names)

    def _load_files(self) -> None:
        if self.importers is not None:
            return
        from importers.alignment import AlignmentImporter

        self.importers = {item.path: item for item in AlignmentImporter.finder(self.config, **self.parents)}

    def _get_importer(self, valid_suffix: list[str]) -> BaseImporter | None:
        self._load_files()
        for key, val in self.importers.items():
            if key.endswith(tuple(valid_suffix)):
                return val
        return None

    def _get_tlt_importer(self) -> BaseImporter | None:
        return self._get_importer([".tlt"])

    def _get_tltx_importer(self):
        return self._get_importer([".tltx", ".xtilt"])

    def _get_xf_importer(self) -> BaseImporter | None:
        return self._get_importer([".xf"])

    def get_xf_data(self, xf_data: pd.DataFrame, index: int) -> dict:
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
    path: str,
    parents: dict[str, Any],
) -> BaseAlignmentConverter:
    alignment_format = metadata.get("format")
    if alignment_format == "IMOD":
        return IMODAlignmentConverter(path, config, parents)

    return BaseAlignmentConverter()
