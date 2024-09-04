import os.path
from typing import TYPE_CHECKING

import pandas as pd

from common.finders import DefaultImporterFactory
from common.metadata import AlignmentMetadata
from importers.base_importer import BaseFileImporter

if TYPE_CHECKING:
    TomogramImporter = "TomogramImporter"
else:
    from importers.tomogram import TomogramImporter


class AlignmentImporter(BaseFileImporter):
    type_key = "alignment"
    plural_key = "alignments"
    finder_factory = DefaultImporterFactory
    has_metadata = True

    def import_item(self) -> None:
        pass

    def import_metadata(self) -> None:
        try:
            meta = AlignmentMetadata(self.config.fs, self.get_deposition().name, self.get_base_metadata())
            meta.write_metadata(self.get_metadata_path(), self.get_extra_metadata())
        except IOError:
            print("Not writing metadata for alignment with no source tomogram")

    def get_output_path(self) -> str:
        output_directory = super().get_output_path()
        return os.path.join(output_directory, "id-")

    def get_metadata_path(self) -> str:
        return self.get_output_path() + "alignment_metadata.json"

    def get_extra_metadata(self) -> dict:
        return {
            "volume_dimension": self.get_tomogram_volume_dimension(),
            "per_section_alignment_parameters": self.get_per_section_alignment_parameters(),
            "alignment_path": None,
            "tilt_path": None,
            "tiltx_path": None,
        }

    def get_tomogram_volume_dimension(self) -> dict:
        for tomogram in TomogramImporter.finder(self.config, **self.parents):
            return tomogram.get_source_volume_info().get_dimensions()

        if self.is_default_alignment():
            raise IOError("No source tomogram found for creating default alignment")

        print("No source tomogram found for alignment, setting volume dimension to default")
        return {"x": None, "y": None, "z": None}

    def get_per_section_alignment_parameters(self) -> list:
        result = []
        if self.is_default_alignment():
            return result
        xf_data = self.get_xf_data()
        tlt_data = self.get_tlt_data()
        tltx_data = self.get_tltx_data()
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

    def is_default_alignment(self) -> bool:
        return self.name.lower() == "default"

    def get_xf_data(self) -> pd.DataFrame:
        file_type = os.path.splitext(self.path)
        if file_type[1] == ".xf":
            local_path = self.config.fs.localreadable(self.path)
            return pd.read_csv(
                local_path,
                sep=r"\s+",
                header=None,
                names=["rotation_0", "rotation_1", "rotation_2", "rotation_3", "x_offset", "y_offset"],
            )
        print(f"Alignment file of {file_type} not supported")
        return pd.DataFrame()

    def get_tlt_data(self) -> pd.DataFrame:
        return pd.DataFrame()

    def get_tltx_data(self) -> pd.DataFrame:
        return pd.DataFrame()
