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
        voxel_size = self.parent.get_voxel_spacing()
        resolution = (voxel_size * 1e-10, voxel_size * 1e-10, voxel_size * 1e-10)
        volume_header = self.parent.get_output_header()
        run_name = self.parent.get_run().run_name

        image_layer = state_generator.generate_image_layer(
            zarr_dir_path,
            scale=resolution,
            url=self.config.https_prefix,
            size={d: volume_header[f"n{d}"].item() for d in "xyz"},
            name=run_name,
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
                hex_colors, float_colors = colors.get_hex_colors(1, exclude=colors_used)
                if isinstance(source, annotation.SegmentationMaskFile):
                    source_path = (
                        source.get_output_filename(output_prefix, "zarr")
                        .removeprefix(self.config.output_prefix)
                        .removeprefix("/")
                    )
                    layer = state_generator.generate_image_volume_layer(
                        source_path,
                        f"{anno.identifier} {name} segmentation",
                        self.config.https_prefix,
                        color=hex_colors[0],
                        scale=resolution,
                        is_visible=source.is_visualization_default,
                        rendering_depth=15000,
                    )
                    colors_used.append(float_colors[0])
                    layers.append(layer)
                elif isinstance(source, annotation.PointFile):
                    ng_output_path = self.config.resolve_output_path("neuroglancer_precompute", run_name, voxel_size)
                    source_path = (
                        source.get_neuroglancer_precompute_path(output_prefix, ng_output_path)
                        .removeprefix(self.config.output_prefix)
                        .removeprefix("/")
                    )
                    is_instance_segmentation = type(source) is annotation.InstanceSegmentationFile
                    layer = state_generator.generate_point_layer(
                        source_path,
                        f"{anno.identifier} {name} point",
                        self.config.https_prefix,
                        color=hex_colors,
                        scale=resolution,
                        is_visible=source.is_visualization_default,
                        is_instance_segmentation=is_instance_segmentation,
                    )
                    if is_instance_segmentation:
                        colors_used.append(float_colors[0])
                    layers.append(layer)

        return state_generator.combine_json_layers(layers, scale=resolution)

    @classmethod
    def find_ng(cls, config: DataImportConfig, tomo: TomogramImporter) -> list["NeuroglancerImporter"]:
        return [cls(config=config, parent=tomo)]
