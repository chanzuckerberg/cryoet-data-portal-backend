import os.path
from typing import TYPE_CHECKING

import pandas as pd

from common.finders import DefaultImporterFactory
from common.metadata import AlignmentMetadata
from importers.base_importer import BaseFileImporter, BaseImporter
from importers.tilt import TiltImporter

if TYPE_CHECKING:
    TomogramImporter = "TomogramImporter"
else:
    from importers.tomogram import TomogramImporter


class AlignmentImporter(BaseFileImporter):
    type_key = "alignment"
    plural_key = "alignments"
    finder_factory = DefaultImporterFactory
    has_metadata = True

    def get_dest_filename(self) -> str:
        output_dir = self.get_output_path()
        return f"{output_dir}{os.path.basename(self.path)}"

    def import_metadata(self) -> None:
        try:
            meta = AlignmentMetadata(self.config.fs, self.get_deposition().name, self.get_base_metadata())
            meta.write_metadata(self.get_metadata_path(), self.get_extra_metadata())
        except IOError:
            print("Skipping creating metadata for default alignment with no source tomogram")

    def get_output_path(self) -> str:
        output_directory = super().get_output_path()
        return os.path.join(output_directory, "id-")

    def get_metadata_path(self) -> str:
        return self.get_output_path() + "alignment_metadata.json"

    def get_extra_metadata(self) -> dict:
        tlt_importer, tltx_importer = self.get_tlt_importers()
        return {
            "volume_dimension": self.get_tomogram_volume_dimension(),
            "per_section_alignment_parameters": self.get_per_section_alignment_parameters(tlt_importer, tltx_importer),
            "alignment_path": self.get_dest_filename(),
            "tilt_path": tlt_importer.get_dest_filename() if tlt_importer else None,
            "tiltx_path": tltx_importer.get_dest_filename() if tltx_importer else None,
        }

    def get_tomogram_volume_dimension(self) -> dict:
        for tomogram in TomogramImporter.finder(self.config, **self.parents):
            return tomogram.get_source_volume_info().get_dimensions()

        if self.is_default_alignment():
            raise IOError("No source tomogram found for creating default alignment")

        print("No source tomogram found for alignment, setting volume dimension to default")
        return {"x": None, "y": None, "z": None}

    def get_per_section_alignment_parameters(
        self, tlt_importer: BaseFileImporter, tltx_importer: BaseFileImporter,
    ) -> list:
        result = []
        if self.is_default_alignment():
            return result
        xf_data = self.get_xf_data()
        tlt_data = self.get_dataframe(tlt_importer, ["tilt_angle"])
        tltx_data = self.get_dataframe(tltx_importer, ["volume_x_rotation"])
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
            column_names = ["rotation_0", "rotation_1", "rotation_2", "rotation_3", "x_offset", "y_offset"]
            return self.get_dataframe(self, column_names)
        print(f"Alignment file of {file_type} not supported")
        return pd.DataFrame()

    def get_dataframe(self, importer: BaseImporter, names: list[str]) -> pd.DataFrame:
        if not importer:
            return pd.DataFrame()
        local_path = self.config.fs.localreadable(importer.path)
        return pd.read_csv(local_path, sep=r"\s+", header=None, names=names)

    def get_tlt_importers(self) -> [BaseFileImporter, BaseFileImporter]:
        tlt_importer = tltx_importer = None
        for importer in TiltImporter.finder(self.config, **self.parents):
            source_filename = os.path.basename(importer.path)
            if source_filename.endswith(".tlt"):
                tlt_importer = importer
            elif source_filename.endswith(".tltx"):
                tltx_importer = importer
        return tlt_importer, tltx_importer
