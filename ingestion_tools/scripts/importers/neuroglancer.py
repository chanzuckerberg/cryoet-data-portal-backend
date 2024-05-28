from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

import numpy as np

from common.config import DepositionImportConfig
from common.finders import DefaultImporterFactory
from common.metadata import NeuroglancerMetadata
from importers.base_importer import BaseImporter

if TYPE_CHECKING:
    from importers.tomogram import TomogramImporter
    from common.image import VolumeInfo
else:
    TomogramImporter = "TomogramImporter"
    VolumeInfo = "VolumeInfo"


class NeuroglancerImporter(BaseImporter):
    type_key = "neuroglancer"
    plural_key = "neuroglancer"
    finder_factory = DefaultImporterFactory
    has_metadata = False

    def import_item(self) -> str:
        dest_file = self.get_output_path()
        ng_contents = self.get_config_json(self.get_tomogram().get_output_path() + ".zarr")
        meta = NeuroglancerMetadata(self.config.fs, self.config.deposition_id, ng_contents)
        meta.write_metadata(dest_file)
        return dest_file

    def get_config_json(self, zarr_dir: str) -> dict[str, Any]:
        zarr_dir_url_path = zarr_dir.removeprefix(self.config.output_prefix)
        zarr_url = urljoin(self.config.https_prefix, zarr_dir_url_path)
        voxel_size = self.get_voxel_spacing().as_float()
        volume_info = self.get_tomogram().get_output_volume_info()
        dimensions = {k: [voxel_size * 1e-10, "m"] for k in "xyz"}
        return {
            "dimensions": dimensions,
            "position": self.get_position(volume_info),
            "crossSectionScale": self.get_cross_section_scale(volume_info),
            "crossSectionBackgroundColor": "#000000",
            "layers": [
                {
                    "type": "image",
                    "source": f"zarr://{zarr_url}",
                    "opacity": 0.51,
                    "shader": "#uicontrol invlerp normalized\n\nvoid main() {\n  emitGrayscale(normalized());\n}\n",
                    "shaderControls": self.get_shader_controller(volume_info),
                    "name": "tomogram",
                },
            ],
            "selectedLayer": {"visible": True, "layer": "tomogram"},
            "layout": "4panel",
        }

    @classmethod
    def get_cross_section_scale(cls, vol_info: VolumeInfo) -> float:
        avg_cross_section_render_height = 400
        largest_dimension = vol_info.get_max_dimension()
        return max(largest_dimension / avg_cross_section_render_height, 1)

    @classmethod
    def get_position(cls, vol_info: VolumeInfo) -> list[float]:
        return vol_info.get_center_coords()

    @classmethod
    def get_shader_controller(cls, vol_info: VolumeInfo) -> dict[str, Any]:
        width = 3 * vol_info.rms

        mean = vol_info.dmean
        start = mean - width
        end = mean + width

        window_width_factor = width * 0.1
        window_start = start - window_width_factor
        window_end = end + window_width_factor

        return {
            "normalized": {
                "range": [start, end],
                "window": [window_start, window_end],
            },
        }

    @classmethod
    def find_ng(cls, config: DepositionImportConfig, tomo: TomogramImporter) -> list["NeuroglancerImporter"]:
        return [cls(config=config, parent=tomo)]
