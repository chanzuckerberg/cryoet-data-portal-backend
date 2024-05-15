from typing import TYPE_CHECKING, Any

import cryoet_data_portal_neuroglancer.state_generator as state_generator

from common import colors
from common.config import DataImportConfig
from common.metadata import NeuroglancerMetadata
from importers import annotation
from importers.annotation import AnnotationImporter
from importers.base_importer import BaseImporter

if TYPE_CHECKING:
    from importers.tomogram import TomogramImporter
else:
    TomogramImporter = "TomogramImporter"


class NeuroglancerImporter(BaseImporter):
    type_key = "neuroglancer"

    def import_neuroglancer(self, annotations: list[AnnotationImporter]) -> str:
        dest_file = self.get_output_path()
        tomogram_zarr_dir = self.parent.get_output_path() + ".zarr"
        ng_contents = self.create_config_json(tomogram_zarr_dir, annotations)
        meta = NeuroglancerMetadata(self.config.fs, ng_contents)
        meta.write_metadata(dest_file)
        return dest_file

    def create_config_json(self, zarr_dir: str, annotations: list[AnnotationImporter]) -> dict[str, Any]:
        zarr_dir_path = zarr_dir.removeprefix(self.config.output_prefix).removeprefix("/")
        voxel_size = self.parent.get_voxel_spacing() * 1e-10
        resolution = (voxel_size, voxel_size, voxel_size)
        volume_header = self.parent.get_output_header()
        image_layer = state_generator.generate_image_layer(
            zarr_dir_path,
            resolution=resolution,
            url=self.config.https_prefix,
            size={d: volume_header[f"n{d}"].item() for d in "xyz"},
            name=self.parent.get_run().run_name,
            mean=volume_header.dmean.item(),
            rms=volume_header.rms.item(),
            start={d: volume_header[f"n{d}start"].item() for d in "xyz"},
        )
        layers = [image_layer]
        colors_used = []
        for anno in annotations:
            output_prefix = anno.get_output_path()
            name = anno.metadata.get("annotation_object", {}).get("name")
            for source in anno.sources:
                if isinstance(source, annotation.SegmentationMaskFile):
                    hex_colors, float_colors = colors.get_hex_colors(1, exclude=colors_used)
                    source_path = (
                        source.get_output_filename(output_prefix, "zarr")
                        .removeprefix(self.config.output_prefix)
                        .removeprefix("/")
                    )
                    layer = state_generator.generate_image_volume_layer(
                        source_path,
                        f"{name}-segmentation",
                        self.config.https_prefix,
                        color=hex_colors[0],
                        resolution=resolution,
                        is_visible=source.is_visualization_default,
                    )
                    colors_used.append(float_colors[0])
                    layers.append(layer)

        return state_generator.combine_json_layers(layers, resolution=resolution)

    @classmethod
    def find_ng(cls, config: DataImportConfig, tomo: TomogramImporter) -> list["NeuroglancerImporter"]:
        return [cls(config=config, parent=tomo)]
