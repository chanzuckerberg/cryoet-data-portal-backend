import json
import os.path
from pathlib import Path
from typing import TYPE_CHECKING, Any

import cryoet_data_portal_neuroglancer.state_generator as state_generator

from common import colors
from common.config import DataImportConfig
from common.metadata import NeuroglancerMetadata
from importers.base_importer import BaseImporter

if TYPE_CHECKING:
    from importers.tomogram import TomogramImporter
else:
    TomogramImporter = "TomogramImporter"


class NeuroglancerImporter(BaseImporter):
    type_key = "neuroglancer"

    def import_neuroglancer_config(self) -> str:
        dest_file = self.get_output_path()
        tomogram_zarr_dir = self.parent.get_output_path() + ".zarr"
        ng_contents = self.create_config_json(tomogram_zarr_dir)
        meta = NeuroglancerMetadata(self.config.fs, ng_contents)
        meta.write_metadata(dest_file)
        return dest_file

    def create_config_json(self, zarr_dir: str) -> dict[str, Any]:
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

        ng_output_path = self.config.resolve_output_path("neuroglancer_precompute", run_name, voxel_size)
        annotation_metadata_paths = self._get_annotation_metadata_files(run_name, voxel_size)
        for annotation_metadata_path in annotation_metadata_paths:
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
                    source_path = os.path.join(ng_output_path, f"{stemmed_metadata_path}_{shape.lower()}").removeprefix(
                        self.config.output_prefix,
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
    def find_ng(cls, config: DataImportConfig, tomo: TomogramImporter) -> list["NeuroglancerImporter"]:
        return [cls(config=config, parent=tomo)]

    def _get_path(self, key: str, run_name: str, voxel_size: str) -> str:
        return self.config.resolve_output_path(key, run_name, voxel_size)

    def _get_annotation_metadata_files(self, run_name: str, voxel_size: float) -> list[str]:
        annotation_path = self._get_path("annotation_metadata", run_name, "{:.3f}".format(voxel_size))
        pattern = os.path.join(annotation_path, "*.json")
        return self.config.fs.glob(pattern)
