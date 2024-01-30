from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

from common.config import DataImportConfig
from common.metadata import NeuroglancerMetadata

from importers.base_importer import BaseImporter

if TYPE_CHECKING:
    from importers.tomogram import TomogramImporter
else:
    TomogramImporter = "TomogramImporter"


class NeuroglancerImporter(BaseImporter):
    type_key = "neuroglancer"

    def import_neuroglancer(self):
        dest_file = self.get_output_path()
        ng_contents = self.get_config_json(self.parent.get_output_path() + ".zarr")
        meta = NeuroglancerMetadata(self.config.fs, ng_contents)
        meta.write_metadata(dest_file)
        return dest_file

    def get_config_json(self, tomo_zarr_dir: str) -> dict[str, Any]:
        tomo_zarr_dir_url_path = tomo_zarr_dir.removeprefix(self.config.output_prefix)
        zarr_url = urljoin(self.config.https_prefix, tomo_zarr_dir_url_path)
        voxel_size = self.parent.get_voxel_spacing()
        dimensions = {k: [voxel_size * 10e-10, "m"] for k in "xyz"}
        return {
            "dimensions": {
                "z": [1, ""],
                "y": [1, ""],
                "x": [1, ""],
            },
            "layers": [
                {
                    "type": "image",
                    "source": f"zarr://{zarr_url}",
                    "opacity": 0.51,
                    "shader": "#uicontrol invlerp normalized\n\nvoid main() {\n  emitGrayscale(normalized());\n}\n",
                    "shaderControls": self.get_shader_controller(),
                    "name": "tomogram",
                    "transform": {
                        "outputDimensions": dimensions,
                        "inputDimensions": dimensions,
                    },
                }
            ],
            "selectedLayer": {"visible": True, "layer": "tomogram"},
            "layout": "4panel",
        }

    def get_shader_controller(self):
        tomo_header = self.parent.get_output_header()
        width = 3 * tomo_header.rms.item()

        mean = tomo_header.dmean.item()
        start = mean - width
        end = mean + width

        window_width_factor = width * 0.1
        window_start = start - window_width_factor
        window_end = end + window_width_factor

        return {
            "normalized": {
                "range": [start, end],
                "window": [window_start, window_end],
            }
        }

    @classmethod
    def find_ng(cls, config: DataImportConfig, tomo: TomogramImporter) -> list["NeuroglancerImporter"]:
        return [cls(config=config, parent=tomo)]
