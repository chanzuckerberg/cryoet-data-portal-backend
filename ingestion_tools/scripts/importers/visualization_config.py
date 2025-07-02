import json
import os.path
from pathlib import Path
from time import time
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
        if not tomogram.get_base_metadata().get("is_visualization_default"):
            print("Skipping import for tomogram that is not configured for default_visualization")
            return
        ng_contents = self._create_config(tomogram.alignment_metadata_path)
        meta = NeuroglancerMetadata(self.config.fs, self.get_deposition().name, ng_contents)
        meta.write_metadata(self.get_output_path())

    def _get_annotation_metadata_files(self) -> list[str]:
        # Getting a list of paths to the annotation metadata files using glob instead of using the annotation finder
        # to get all the annotations and not just the ones associated with the current deposition
        annotation_path = self.config.resolve_output_path("annotation_metadata", self, {"annotation_id": "*"})
        return self.config.fs.glob(os.path.join(annotation_path, "*.json"))

    def _to_tomogram_layer(
        self,
        tomogram: TomogramImporter,
        volume_info: VolumeInfo,
        resolution: tuple[float, float, float],
        contrast_limits: tuple[float, float],
    ) -> dict[str, Any]:
        zarr_dir_path = self.config.to_formatted_path(f"{tomogram.get_output_path()}.zarr")
        return state_generator.generate_image_layer(
            zarr_dir_path,
            scale=resolution,
            url=self.config.https_prefix,
            size=volume_info.get_dimensions(),
            name=self.get_run().name,
            mean=volume_info.dmean,
            rms=volume_info.rms,
            start={d: getattr(volume_info, f"{d}start") for d in "xyz"},
            threedee_contrast_limits=contrast_limits,
        )

    def _to_segmentation_mask_layer(
        self,
        source_path: str,
        file_metadata: dict[str, Any],
        name_prefix: str,
        color: str,
        resolution: tuple[float, float, float],
        display_mesh: bool,
        **kwargs,
    ) -> dict[str, Any]:
        return state_generator.generate_segmentation_mask_layer(
            source=source_path,
            name=f"{name_prefix} segmentation",
            url=self.config.https_prefix,
            color=color,
            scale=resolution,
            is_visible=file_metadata.get("is_visualization_default"),
            display_mesh=display_mesh,
        )

    def _to_point_layer(
        self,
        source_path: str,
        file_metadata: dict[str, Any],
        name_prefix: str,
        color: str,
        resolution: tuple[float, float, float],
        shape: str,
        **kwargs,
    ) -> dict[str, Any]:
        is_instance_segmentation = shape == "InstanceSegmentation"
        args = {
            "source": source_path,
            "url": self.config.https_prefix,
            "color": color,
            "scale": resolution,
            "is_visible": file_metadata.get("is_visualization_default"),
            "is_instance_segmentation": is_instance_segmentation,
        }
        if shape == "OrientedPoint":
            args["name"] = f"{name_prefix} orientedpoint"
            return state_generator.generate_oriented_point_layer(**args)
        args["name"] = f"{name_prefix} point"
        return state_generator.generate_point_layer(**args)

    def get_annotation_layer_info(self, alignment_metadata_path: str) -> dict[str, Any]:
        precompute_path = self.config.resolve_output_path("annotation_viz", self)

        # TODO: Update the annotation metadata to be fetched from all voxel spacings once, we start supporting the
        #  co-ordinate transformation in neuroglancer
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

                path = self.config.to_formatted_path(
                    os.path.join(precompute_path, f"{metadata_file_name}_{shape.lower()}"),
                )

                is_instance_seg = shape == "InstanceSegmentation"

                annotation_layer_info[file.get("path")] = {
                    "shape": shape,
                    "args": {
                        "source_path": path,
                        "file_metadata": file,
                        "name_prefix": name_prefix,
                        "color": hex_colors[0],
                        "shape": shape,
                    },
                }

                if not is_instance_seg:
                    colors_used.append(float_colors[0])

        return annotation_layer_info

    def _to_mesh_layer(
        self,
        source_path: str,
        file_metadata: dict[str, Any],
        name_prefix: str,
        color: str,
        resolution: tuple[float, float, float],
        **_,
    ):
        args = {
            "name": f"{name_prefix} orientedmesh",
            "source": source_path.replace("_orientedpoint", "_orientedmesh"),
            "url": self.config.https_prefix,
            "color": color,
            "scale": resolution,
            "is_visible": file_metadata.get("is_visualization_default"),
        }

        return state_generator.generate_oriented_point_mesh_layer(**args)

    def _has_mesh(self, path: str):
        fs = self.config.fs
        mesh_folder_path = Path(self.config.output_prefix) / path.replace("_orientedpoint", "_orientedmesh").replace(
            "_segmentationmask", "_orientedmesh",
        )
        return fs.exists(f"{mesh_folder_path}")

    def _create_config(self, alignment_metadata_path: str) -> dict[str, Any]:
        tomogram = self.get_tomogram()
        volume_info = tomogram.get_output_volume_info()
        voxel_size = round(volume_info.voxel_size, 3)
        resolution = (voxel_size * 1e-10,) * 3
        # we display information about when the contrast limit computation starts and finishes
        # to give feedback to the user why the script is hanging as the computation limit might
        # take time depending on use pyramid level as well as the used computation method.
        t = time()
        print("Start contrast limit computation for", tomogram)
        contrast_limits = tomogram.get_contrast_limits()
        print(f"Computed contrast limit {contrast_limits} in  {(time() - t):.2f}s")
        layers = [self._to_tomogram_layer(tomogram, volume_info, resolution, contrast_limits)]

        annotation_layer_info = self.get_annotation_layer_info(alignment_metadata_path)

        for _, info in annotation_layer_info.items():
            args = {**info["args"], "resolution": resolution}
            has_mesh = self._has_mesh(args["source_path"])
            shape = info["shape"]
            if shape == "SegmentationMask":
                if has_mesh:
                    print(
                        f"Segmentation layer {args['name_prefix']} as oriented mesh, disabling segmentation mesh display",
                    )
                args = {**args, "display_mesh": not has_mesh}
                layers.append(self._to_segmentation_mask_layer(**args))
            elif shape in {"Point", "OrientedPoint", "InstanceSegmentation"}:
                layers.append(self._to_point_layer(**args))
                if shape == "OrientedPoint" and has_mesh:
                    layers.append(self._to_mesh_layer(**args))
        return state_generator.combine_json_layers(layers, scale=resolution)

    @classmethod
    def _get_annotation_name_prefix(cls, metadata: dict[str, Any], stemmed_metadata_path: str) -> str:
        name = metadata.get("annotation_object", {}).get("name", "Annotation")
        anno_identifier = int(stemmed_metadata_path.split("-")[0])
        return f"{anno_identifier} {name}"

    @classmethod
    def get_default_config(cls) -> list[dict] | None:
        return [{"sources": [{"literal": {"value": ["neuroglancer"]}}]}]
