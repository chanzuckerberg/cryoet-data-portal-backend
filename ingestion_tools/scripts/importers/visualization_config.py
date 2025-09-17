import json
import os.path
from pathlib import Path
from time import time
from typing import TYPE_CHECKING, Any, cast

import cryoet_data_portal_neuroglancer.state_generator as state_generator

from common import colors
from common.colors import generate_hash, to_base_hash_input
from common.finders import DefaultImporterFactory
from common.image import VolumeInfo
from common.metadata import NeuroglancerMetadata
from importers.annotation import OrientedPointAnnotation
from importers.base_importer import BaseImporter
from importers.visualization_precompute import get_annotation_neuroglancer_precompute_path

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
        contrast_limits: tuple[float, float],
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
            threedee_contrast_limits=contrast_limits,
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
        visible: bool | None = None,
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
            "is_visible": file_metadata.get("is_visualization_default") if visible is None else visible,
            "is_instance_segmentation": is_instance_segmentation,
        }
        if shape == "OrientedPoint":
            args["name"] = f"{name_prefix} orientedpoint"
            return state_generator.generate_oriented_point_layer(**args)
        args["name"] = f"{name_prefix} point"
        return state_generator.generate_point_layer(**args)

    def _to_triangular_mesh_layer(
        self,
        source_path: str,
        file_metadata: dict[str, Any],
        name_prefix: str,
        color: str,
        resolution: tuple[float, float, float],
        **kwargs,
    ) -> dict[str, Any]:
        return state_generator.generate_mesh_layer(
            source=source_path,
            name=f"{name_prefix} mesh",
            url=self.config.https_prefix,
            color=color,
            scale=resolution,
            is_visible=file_metadata.get("is_visualization_default"),
        )

    def _find_annotation_metadata(self, precomputed_output_path: str, shape: str) -> tuple[str, float, float] | None:
        """
        Find the real path to a metadata file.

        If the file for the current voxel spacing doesn't exist,
        try matching files across all possible voxel spacings.
        Returns a tuple of (file_path, voxel_spacing_float, ratio) or None if no match is found.
        """
        voxel_spacing = self.get_voxel_spacing().as_float()

        if self.config.fs.exists(precomputed_output_path):
            return precomputed_output_path, voxel_spacing, 1.0

        # Try finding matching files across all voxel spacings
        voxel_spacing_name = self.get_voxel_spacing().name
        base_dir = Path(self.config.resolve_output_path("voxel_spacing", self)).parent
        file_glob = precomputed_output_path.replace(f"VoxelSpacing{voxel_spacing_name}", "VoxelSpacing*")
        matched_files = self.config.fs.glob(file_glob)

        if not matched_files:
            return None

        if len(matched_files) > 1:
            print(f"Multiple files found for {precomputed_output_path}, using the first one")

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

            for file in metadata.get("files", []):
                shape = file.get("shape")
                if shape not in {
                    "SegmentationMask",
                    "Point",
                    "OrientedPoint",
                    "InstanceSegmentation",
                    "TriangularMesh",
                    "TriangularMeshGroup",
                }:
                    print(f"Skipping file with unknown shape {shape}")
                    continue
                output_annotation_path = get_annotation_neuroglancer_precompute_path(
                    str(Path(annotation_metadata_path).with_suffix("")),
                    self.config.resolve_output_path("annotation_viz", self),
                    shape,
                )
                metadata_file_name = Path(output_annotation_path).stem
                name_prefix = self._get_annotation_name_prefix(metadata, metadata_file_name)

                # Skip mrc files as we will only generate layers for zarr volumes and ndjson files
                # TODO does this also need to have the other mesh formats listed here?
                # Not entirely sure how the conversion to glb is handled
                if file.get("format") not in {"zarr", "ndjson", "glb"}:
                    print(f"Skipping file with unsupported format {file.get('format')}")
                    continue

                color_seed = generate_hash({**annotation_hash_input, **{"shape": shape}})
                hex_colors, float_colors = colors.get_hex_colors(1, exclude=colors_used, seed=color_seed)

                result = self._find_annotation_metadata(output_annotation_path, shape)
                if result is None:
                    print(f"Skipping annotation {output_annotation_path} for shape {shape} as no matching file found")
                    continue
                file_path, voxel_spacing, ratio = result
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

    def _to_mesh_layer(
        self,
        source_path: str,
        file_metadata: dict[str, Any],
        name_prefix: str,
        color: str,
        resolution: tuple[float, float, float],
        **_,
    ):
        return state_generator.generate_oriented_point_mesh_layer(
            name=f"{name_prefix} orientedmesh",
            source=OrientedPointAnnotation.convert_oriented_point_path_to_mesh_path(source_path),
            url=self.config.https_prefix,
            color=color,
            scale=resolution,
            is_visible=cast(bool, file_metadata.get("is_visualization_default")),
        )

    def _has_oriented_mesh(self, path: str):
        fs = self.config.fs
        oriented_mesh_filename = OrientedPointAnnotation.convert_oriented_point_path_to_mesh_path(path)
        mesh_folder_path = os.path.join(self.config.output_prefix, oriented_mesh_filename)
        return fs.exists(mesh_folder_path)

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
        largest_ratio = 1.0

        for _, info in annotation_layer_info.items():
            shape = info["shape"]
            args = {**info["args"], "output_resolution": resolution}
            if shape == "SegmentationMask":
                layers.append(self._to_segmentation_mask_layer(**args))
            elif shape in {"Point", "OrientedPoint", "InstanceSegmentation"}:
                if shape == "OrientedPoint":
                    # Check if oriented point has produced meshes
                    has_mesh = self._has_oriented_mesh(args["source_path"])
                    if has_mesh:
                        layers.append(self._to_mesh_layer(**args))
                        print(
                            f"{shape} {args['name_prefix']} has meshes -> hiding raw {shape} layer in neuroglancer in favor of mesh layer",
                        )
                        args = {**args, "visible": False}
                layers.append(self._to_point_layer(**args))
            elif info["shape"] in {"TriangularMesh", "TriangularMeshGroup"}:
                layers.append(self._to_triangular_mesh_layer(**args))

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
