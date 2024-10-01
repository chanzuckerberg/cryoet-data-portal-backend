import json
import os.path
from pathlib import Path
from typing import TYPE_CHECKING, Any

import cryoet_data_portal_neuroglancer.state_generator as state_generator

from common import colors
from common.colors import generate_hash, to_base_hash_input
from common.finders import DefaultImporterFactory
from common.image import VolumeInfo
from common.metadata import NeuroglancerMetadata
from importers.base_importer import BaseImporter

if TYPE_CHECKING:
    from importers.tomogram import TomogramImporter
else:
    TomogramImporter = "TomogramImporter"


class VisualizationConfigImporter(BaseImporter):
    type_key = "viz_config"
    plural_key = "viz_config"
    finder_factory = DefaultImporterFactory
    has_metadata = False
    dir_path = (
        "{dataset_name}/{run_name}/Tomograms/VoxelSpacing{voxel_spacing_name}/NeuroglancerPrecompute/"
        "{{identifier}}-neuroglancer_config.json"
    )

    def import_item(self) -> None:
        if not self.is_import_allowed():
            print(f"Skipping import of {self.name}")
            return
        if not self.get_tomogram().metadata.get("is_visualization_default"):
            print("Skipping import for tomogram that is not configured for default_visualization")
            return
        ng_contents = self._create_config()
        meta = NeuroglancerMetadata(self.config.fs, self.get_deposition().name, ng_contents)
        meta.write_metadata(self.get_output_path())

    def get_output_path(self) -> str:
        return super().get_output_path().format(identifier=self.get_tomogram().get_identifier())

    def _get_annotation_metadata_files(self) -> list[str]:
        # Getting a list of paths to the annotation metadata files using glob instead of using the annotation finder
        # to get all the annotations and not just the ones associated with the current deposition
        annotation_path = self.config.resolve_output_path("annotation_metadata", self)
        return self.config.fs.glob(os.path.join(annotation_path, "*.json"))

    def _to_directory_path(self, path: str) -> str:
        return path.removeprefix(self.config.output_prefix).removeprefix("/")

    def _to_tomogram_layer(
        self,
        tomogram: TomogramImporter,
        volume_info: VolumeInfo,
        resolution: tuple[float, float, float],
    ) -> dict[str, Any]:
        zarr_dir_path = self._to_directory_path(f"{tomogram.get_output_path()}.zarr")
        return state_generator.generate_image_layer(
            zarr_dir_path,
            scale=resolution,
            url=self.config.https_prefix,
            size=volume_info.get_dimensions(),
            name=self.get_run().name,
            mean=volume_info.dmean,
            rms=volume_info.rms,
            start={d: getattr(volume_info, f"{d}start") for d in "xyz"},
        )

    def _to_segmentation_mask_layer(
        self,
        source_path: str,
        file_metadata: dict[str, Any],
        name_prefix: str,
        color: str,
        resolution: tuple[float, float, float],
    ) -> dict[str, Any]:
        return state_generator.generate_segmentation_mask_layer(
            source_path,
            f"{name_prefix} segmentation",
            self.config.https_prefix,
            color=color,
            scale=resolution,
            is_visible=file_metadata.get("is_visualization_default"),
        )

    def _to_point_layer(
        self,
        source_path: str,
        file_metadata: dict[str, Any],
        name_prefix: str,
        color: str,
        resolution: tuple[float, float, float],
        is_instance_segmentation: bool,
    ) -> dict[str, Any]:
        return state_generator.generate_point_layer(
            source_path,
            f"{name_prefix} point",
            self.config.https_prefix,
            color=color,
            scale=resolution,
            is_visible=file_metadata.get("is_visualization_default"),
            is_instance_segmentation=is_instance_segmentation,
        )

    def _create_config(self) -> dict[str, Any]:
        tomogram = self.get_tomogram()
        volume_info = tomogram.get_output_volume_info()
        voxel_size = round(volume_info.voxel_size, 3)
        resolution = (voxel_size * 1e-10,) * 3
        layers = [self._to_tomogram_layer(tomogram, volume_info, resolution)]

        precompute_path = self.config.resolve_output_path("annotation_viz", self)

        annotation_metadata_paths = self._get_annotation_metadata_files()
        colors_used = []

        for annotation_metadata_path in annotation_metadata_paths:
            with open(self.config.fs.localreadable(annotation_metadata_path), "r") as f:
                metadata = json.load(f)
            annotation_hash_input = to_base_hash_input(metadata)
            metadata_file_name = Path(annotation_metadata_path).stem
            name_prefix = self._get_annotation_name_prefix(metadata, metadata_file_name)

            for file in metadata.get("files", []):
                # Skip mrc files as we will only generate layers for zarr volumes and ndjson files
                if file.get("format") not in {"zarr", "ndjson"}:
                    continue

                shape = file.get("shape")
                color_seed = generate_hash({**annotation_hash_input, **{"shape": shape}})
                hex_colors, float_colors = colors.get_hex_colors(1, exclude=colors_used, seed=color_seed)
                path = self._to_directory_path(
                    os.path.join(precompute_path, f"{metadata_file_name}_{shape.lower()}"),
                )
                if shape == "SegmentationMask":
                    layers.append(self._to_segmentation_mask_layer(path, file, name_prefix, hex_colors[0], resolution))
                    colors_used.append(float_colors[0])
                elif shape in {"Point", "OrientedPoint", "InstanceSegmentation"}:
                    is_instance_seg = shape == "InstanceSegmentation"
                    layer = self._to_point_layer(path, file, name_prefix, hex_colors[0], resolution, is_instance_seg)
                    layers.append(layer)
                    if not is_instance_seg:
                        colors_used.append(float_colors[0])
                else:
                    print(f"Skipping file with unknown shape {shape}")

        return state_generator.combine_json_layers(layers, scale=resolution)

    @classmethod
    def _get_annotation_name_prefix(cls, metadata: dict[str, Any], stemmed_metadata_path: str) -> str:
        name = metadata.get("annotation_object", {}).get("name", "Annotation")
        anno_identifier = int(stemmed_metadata_path.split("-")[0])
        return f"{anno_identifier} {name}"

    @classmethod
    def get_default_config(cls) -> list[dict] | None:
        return [{"sources": [{"literal": {"value": ["neuroglancer"]}}]}]
