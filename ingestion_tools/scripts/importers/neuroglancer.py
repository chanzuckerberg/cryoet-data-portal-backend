import json
import os.path
from pathlib import Path
from typing import TYPE_CHECKING, Any

import cryoet_data_portal_neuroglancer.state_generator as state_generator

from common import colors
from common.config import DepositionImportConfig
from common.finders import DefaultImporterFactory
from common.metadata import NeuroglancerMetadata
from importers.base_importer import BaseImporter

if TYPE_CHECKING:
    from importers.tomogram import TomogramImporter
else:
    TomogramImporter = "TomogramImporter"


class NeuroglancerImporter(BaseImporter):
    type_key = "neuroglancer"
    plural_key = "neuroglancer"
    finder_factory = DefaultImporterFactory
    has_metadata = False

    def import_item(self) -> str:
        dest_file = self.get_output_path()
        ng_contents = self._get_config_json(self.get_tomogram().get_output_path() + ".zarr")
        meta = NeuroglancerMetadata(self.config.fs, self.config.deposition_id, ng_contents)
        meta.write_metadata(dest_file)
        return dest_file

    def _get_annotation_metadata_files(self) -> list[str]:
        annotation_path = self.config.resolve_output_path("annotation_metadata", self)
        return self.config.fs.glob(os.path.join(annotation_path, "*.json"))

    def _get_config_json(self, zarr_dir: str) -> dict[str, Any]:
        zarr_dir_path = zarr_dir.removeprefix(self.config.output_prefix).removeprefix("/")
        voxel_size = self.get_voxel_spacing().as_float()
        resolution = (voxel_size * 1e-10, voxel_size * 1e-10, voxel_size * 1e-10)
        volume_header = self.get_tomogram().get_output_header()
        run_name = self.get_run().name

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

        ng_output_path = self.config.resolve_output_path("neuroglancer_precompute", run_name, voxel_size)
        for annotation_metadata_path in self._get_annotation_metadata_files():
            local_path = self.config.fs.localreadable(annotation_metadata_path)
            with open(local_path, "r") as f:
                metadata = json.load(f)
            stemmed_metadata_path = Path(annotation_metadata_path).stem
            anno_identifier = int(stemmed_metadata_path.split("-")[0])
            name = metadata.get("annotation_object", {}).get("name")
            for file in metadata.get("files", []):
                file_format = file.get("format")
                if file_format == "mrc":
                    continue

                shape = file.get("shape")
                hex_colors, float_colors = colors.get_hex_colors(1, exclude=colors_used)
                if shape == "SegmentationMask":
                    layer = state_generator.generate_image_volume_layer(
                        file.get("path"),
                        f"{anno_identifier} {name} segmentation",
                        self.config.https_prefix,
                        color=hex_colors[0],
                        scale=resolution,
                        is_visible=file.get("is_visualization_default"),
                        rendering_depth=15000,
                    )
                    colors_used.append(float_colors[0])
                    layers.append(layer)
                elif shape in {"Point", "OrientedPoint", "InstanceSegmentation"}:
                    source_path = (
                        os.path.join(ng_output_path, f"{stemmed_metadata_path}_{shape.lower()}")
                        .removeprefix(self.config.output_prefix)
                        .removeprefix("/")
                    )
                    is_instance_segmentation = shape == "InstanceSegmentation"
                    layer = state_generator.generate_point_layer(
                        source_path,
                        f"{anno_identifier} {name} point",
                        self.config.https_prefix,
                        color=hex_colors,
                        scale=resolution,
                        is_visible=file.get("is_visualization_default"),
                        is_instance_segmentation=is_instance_segmentation,
                    )
                    if not is_instance_segmentation:
                        colors_used.append(float_colors[0])
                    layers.append(layer)

        return state_generator.combine_json_layers(layers, scale=resolution)

    @classmethod
    def find_ng(cls, config: DepositionImportConfig, tomo: TomogramImporter) -> list["NeuroglancerImporter"]:
        return [cls(config=config, parent=tomo)]
