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
        "{dataset_name}/{run_name}/Reconstructions/VoxelSpacing{voxel_spacing_name}/NeuroglancerPrecompute/"
        "{tomogram_id}-neuroglancer_config.json"
    )

    def import_item(self) -> None:
        if not self.is_import_allowed():
            print(f"Skipping import of {self.name}")
            return

        tomogram = self.get_tomogram()
        ng_contents = self._create_config(tomogram.alignment_metadata_path)
        meta = NeuroglancerMetadata(self.config.fs, self.get_deposition().name, ng_contents)
        meta.write_metadata(self.get_output_path())

    def _get_annotation_metadata_files(self) -> list[str]:
        # Getting a list of paths to the annotation metadata files using glob instead of using the annotation finder
        # to get all the annotations and not just the ones associated with the current deposition
        annotation_path = self.config.resolve_output_path("annotation_metadata", self, {"annotation_id": "*"})
        # Replace the voxel spacing path with wildcard to get all annotations
        template_path = annotation_path.replace(
            f"VoxelSpacing{self.get_voxel_spacing().name}",
            "VoxelSpacing*",
        )
        return self.config.fs.glob(os.path.join(template_path, "*.json"))

    def _to_tomogram_layer(
        self,
        tomogram: TomogramImporter,
        volume_info: VolumeInfo,
        resolution: tuple[float, float, float],
        output_resolution: tuple[float, float, float] | None = None,
    ) -> dict[str, Any]:
        output_resolution = output_resolution or resolution
        zarr_dir_path = self.config.to_formatted_path(f"{tomogram.get_output_path()}.zarr")
        return state_generator.generate_image_layer(
            zarr_dir_path,
            scale=resolution,
            output_scale=output_resolution,
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
        output_resolution: tuple[float, float, float] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        output_resolution = output_resolution or resolution
        return state_generator.generate_segmentation_mask_layer(
            source=source_path,
            name=f"{name_prefix} segmentation",
            url=self.config.https_prefix,
            color=color,
            scale=resolution,
            output_scale=output_resolution,
            is_visible=file_metadata.get("is_visualization_default"),
        )

    def _to_point_layer(
        self,
        source_path: str,
        file_metadata: dict[str, Any],
        name_prefix: str,
        color: str,
        resolution: tuple[float, float, float],
        shape: str,
        output_resolution: tuple[float, float, float] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        output_resolution = output_resolution or resolution
        is_instance_segmentation = shape == "InstanceSegmentation"
        args = {
            "source": source_path,
            "url": self.config.https_prefix,
            "color": color,
            "scale": resolution,
            "output_scale": output_resolution,
            "is_visible": file_metadata.get("is_visualization_default"),
            "is_instance_segmentation": is_instance_segmentation,
        }
        if shape == "OrientedPoint":
            args["name"] = f"{name_prefix} orientedpoint"
            return state_generator.generate_oriented_point_layer(**args)
        args["name"] = f"{name_prefix} point"
        return state_generator.generate_point_layer(**args)

    def _find_annotation_metadata(self, metadata_file_name: str, shape: str) -> tuple[str, float, float] | None:
        """
        Find the real path to a metadata file.

        If the file for the current voxel spacing doesn't exist,
        try matching files across all possible voxel spacings.
        Returns a tuple of (file_path, voxel_spacing_float, ratio) or None if no match is found.
        """
        precompute_path = self.config.resolve_output_path("annotation_viz", self)
        shape_suffix = shape.lower()
        file_path = os.path.join(precompute_path, f"{metadata_file_name}_{shape_suffix}")
        voxel_spacing = self.get_voxel_spacing().as_float()

        if self.config.fs.exists(file_path):
            return file_path, voxel_spacing, 1.0

        # Try finding matching files across all voxel spacings
        voxel_spacing_name = self.get_voxel_spacing().name
        base_dir = Path(self.config.resolve_output_path("voxel_spacing", self)).parent
        file_glob = file_path.replace(f"VoxelSpacing{voxel_spacing_name}", "VoxelSpacing*")
        matched_files = self.config.fs.glob(file_glob)

        if not matched_files:
            print(f"File {file_path} not found, skipping annotation {metadata_file_name}")
            return None

        if len(matched_files) > 1:
            print(f"Multiple files found for {file_path}, using the first one")

        matched_file_path = matched_files[0]
        try:
            relative_path = Path(matched_file_path).relative_to(base_dir)
        except ValueError:
            print(f"File {matched_file_path} is not relative to the base directory {base_dir}, skipping")
            return None
        voxel_spacing_str = relative_path.parts[0].lstrip("VoxelSpacing")
        new_voxel_spacing = round(float(voxel_spacing_str), 3)
        ratio = new_voxel_spacing / voxel_spacing

        return matched_file_path, new_voxel_spacing, ratio

    def get_annotation_layer_info(self, alignment_metadata_path: str) -> dict[str, Any]:
        annotation_metadata_paths = self._get_annotation_metadata_files()
        colors_used = []

        # Accumulates any arguments that need to be passed to the layer generation functions
        annotation_layer_info = {}

        for annotation_metadata_path in annotation_metadata_paths:
            with open(self.config.fs.localreadable(annotation_metadata_path), "r") as f:
                metadata = json.load(f)
            if metadata.get("alignment_metadata_path") != alignment_metadata_path:
                print(f"Skipping annotation {annotation_metadata_path} with different alignment metadata")
                continue
            annotation_hash_input = to_base_hash_input(metadata)

            metadata_file_name = Path(annotation_metadata_path).stem
            if not metadata_file_name.split("-")[0].isdigit():
                # If the file name does not start with a number, use the id from the directory
                annotation_id = os.path.basename(os.path.dirname(annotation_metadata_path))
                metadata_file_name = f"{annotation_id}-{metadata_file_name}"
            name_prefix = self._get_annotation_name_prefix(metadata, metadata_file_name)

            for file in metadata.get("files", []):
                shape = file.get("shape")
                if shape not in {"SegmentationMask", "Point", "OrientedPoint", "InstanceSegmentation"}:
                    print(f"Skipping file with unknown shape {shape}")
                    continue

                # Skip mrc files as we will only generate layers for zarr volumes and ndjson files
                if file.get("format") not in {"zarr", "ndjson"}:
                    continue

                color_seed = generate_hash({**annotation_hash_input, **{"shape": shape}})
                hex_colors, float_colors = colors.get_hex_colors(1, exclude=colors_used, seed=color_seed)

                file_path, voxel_spacing, ratio = self._find_annotation_metadata(metadata_file_name, shape)

                path = self.config.to_formatted_path(file_path)

                is_instance_seg = shape == "InstanceSegmentation"

                annotation_layer_info[file.get("path")] = {
                    "shape": shape,
                    "voxel_spacing_ratio": ratio,
                    "args": {
                        "source_path": path,
                        "file_metadata": file,
                        "name_prefix": name_prefix,
                        "color": hex_colors[0],
                        "shape": shape,
                        "resolution": (voxel_spacing * 1e-10,) * 3,
                    },
                }

                if not is_instance_seg:
                    colors_used.append(float_colors[0])

        return annotation_layer_info

    def _create_config(self, alignment_metadata_path: str) -> dict[str, Any]:
        tomogram = self.get_tomogram()
        volume_info = tomogram.get_output_volume_info()
        voxel_size = round(volume_info.voxel_size, 3)
        resolution = (voxel_size * 1e-10,) * 3
        layers = [self._to_tomogram_layer(tomogram, volume_info, resolution)]

        annotation_layer_info = self.get_annotation_layer_info(alignment_metadata_path)
        largest_ratio = 1.0

        for _, info in annotation_layer_info.items():
            args = {**info["args"], "output_resolution": resolution}

            if info["shape"] == "SegmentationMask":
                layers.append(self._to_segmentation_mask_layer(**args))
            elif info["shape"] in {"Point", "OrientedPoint", "InstanceSegmentation"}:
                layers.append(self._to_point_layer(**args))
            largest_ratio = max(largest_ratio, info.get("voxel_spacing_ratio", 1.0))

        return state_generator.combine_json_layers(layers, scale=resolution, voxel_size_scale=largest_ratio)

    @classmethod
    def _get_annotation_name_prefix(cls, metadata: dict[str, Any], stemmed_metadata_path: str) -> str:
        name = metadata.get("annotation_object", {}).get("name", "Annotation")
        anno_identifier = int(stemmed_metadata_path.split("-")[0])
        return f"{anno_identifier} {name}"

    @classmethod
    def get_default_config(cls) -> list[dict] | None:
        return [{"sources": [{"literal": {"value": ["neuroglancer"]}}]}]
