import abc
from abc import ABC
from typing import Any

import pandas as pd
from importers.base_importer import BaseImporter

from common.config import DepositionImportConfig


class BaseAlignmentConverter(ABC):
    @abc.abstractmethod
    def get_tilt_path(self) -> str | None:
        """Return a str path to the tilt file if exists else None"""
        pass

    @abc.abstractmethod
    def get_tiltx_path(self) -> str | None:
        """Return a str path to the tiltx file if exists else None"""
        pass

    @abc.abstractmethod
    def get_per_section_alignment_parameters(self) -> list[dict]:
        """Generates the per section alignment parameters"""
        return []


class DefaultAlignmentConverter(BaseAlignmentConverter):
    def get_tilt_path(self) -> str | None:
        return None

    def get_tiltx_path(self) -> str | None:
        return None

    def get_per_section_alignment_parameters(self) -> list[dict]:
        return []


class XfAlignmentConverter(BaseAlignmentConverter):
    def __init__(self, path: str, config: DepositionImportConfig, parents: dict[str, BaseImporter]):
        self.path = path
        self.config = config
        self.parents = parents
        self.importers = None

    def get_tilt_path(self) -> str | None:
        """Return a str path to the tilt file if exists else None"""
        importer = self._get_tlt_importer()
        return importer.get_dest_filename() if importer else None

    def get_tiltx_path(self) -> str | None:
        """Return a str path to the tiltx file if exists else None"""
        importer = self._get_tltx_importer()
        return importer.get_dest_filename() if importer else None

    def get_per_section_alignment_parameters(self) -> list[dict]:
        """Generates the per section alignment parameters"""
        result = []
        xf_data = self._get_xf_data()
        tlt_importer = self._get_tlt_importer()
        tltx_importer = self._get_tltx_importer()
        tlt_data = self._get_dataframe(tlt_importer.path if tlt_importer else None, ["tilt_angle"])
        tltx_data = self._get_dataframe(tltx_importer.path if tltx_importer else None, ["volume_x_rotation"])
        for index, entry in xf_data.iterrows():
            item = {
                "z_index": index,
                "in_plane_rotation": (
                    entry["rotation_0"],
                    entry["rotation_1"],
                    entry["rotation_2"],
                    entry["rotation_3"],
                ),
                "x_offset": entry["x_offset"],
                "y_offset": entry["y_offset"],
                "tilt_angle": None if tlt_data.empty else tlt_data["tilt_angle"][index],
                "volume_x_rotation": 0 if tltx_data.empty else tltx_data["volume_x_rotation"][index],
            }
            result.append(item)
        return result

    def _get_xf_data(self) -> pd.DataFrame:
        column_names = ["rotation_0", "rotation_1", "rotation_2", "rotation_3", "x_offset", "y_offset"]
        return self._get_dataframe(self.path, column_names)

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

    def _get_tlt_importer(self):
        self._load_files()
        for key, val in self.importers.items():
            if key.endswith(".tlt"):
                return val
        return None

    def _get_tltx_importer(self):
        self._load_files()
        for key, val in self.importers.items():
            if key.endswith((".tltx", ".xtilt")):
                return val
        return None


def alignment_converter_factory(
    config: DepositionImportConfig,
    metadata: dict[str, Any],
    path: str,
    parents: dict[str, Any],
) -> BaseAlignmentConverter:
    alignment_format = metadata.get("format")
    if alignment_format == "xf":
        return XfAlignmentConverter(path, config, parents)

    return DefaultAlignmentConverter()
