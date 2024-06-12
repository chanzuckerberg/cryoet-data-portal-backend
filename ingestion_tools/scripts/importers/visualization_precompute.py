import os
from pathlib import Path
from typing import Any

from cryoet_data_portal_neuroglancer.precompute import points, segmentation_mask

from common import colors
from common.config import DepositionImportConfig
from common.finders import DefaultImporterFactory
from importers.annotation import (
    AbstractPointAnnotation,
    BaseAnnotationSource,
    InstanceSegmentationAnnotation,
    VolumeAnnotationSource,
)
from importers.base_importer import BaseImporter


class AnnotationVisualizationImporter(BaseImporter):
    type_key = "annotation_viz"
    plural_key = "annotation_viz"
    finder_factory = DefaultImporterFactory
    has_metadata = False

    def import_item(self) -> None:
        precompute_importer = AnnotationPrecomputeFactory.load(self.get_annotation(), self.config)
        if precompute_importer:
            voxel_spacing = self.get_voxel_spacing().as_float()
            precompute_path = self.get_output_path()
            precompute_importer.neuroglancer_precompute(precompute_path, voxel_spacing)


class BaseAnnotationPrecompute:
    config: DepositionImportConfig

    def __init__(self, annotation: BaseAnnotationSource, config: DepositionImportConfig):
        self.annotation = annotation
        self.config = config

    def _get_shape(self) -> str:
        return self.annotation.shape

    def _get_neuroglancer_precompute_path(self, annotation_path: str, output_prefix: str) -> str:
        file_name = os.path.basename(f"{annotation_path}_{self._get_shape().lower()}")
        return os.path.join(output_prefix, file_name, "")

    def neuroglancer_precompute(self, *args, **kwargs) -> None:
        pass


class AnnotationPrecomputeFactory:
    @classmethod
    def load(cls, annotation: BaseAnnotationSource, config: DepositionImportConfig) -> BaseAnnotationPrecompute | None:
        shape = annotation.shape
        params = {"annotation": annotation, "config": config}
        if shape == "Point":
            return PointAnnotationPrecompute(**params)
        elif shape == "OrientedPoint":
            return OrientedPointAnnotationPrecompute(**params)
        elif shape == "InstanceSegmentation":
            return InstanceSegmentationAnnotationPrecompute(**params)
        elif shape == "SegmentationMask" or shape == "SemanticSegmentationMask":
            return SegmentationMaskAnnotationPrecompute(**params)

        print(f"No precompute for {shape} shape")
        return None


class PointAnnotationPrecompute(BaseAnnotationPrecompute):
    annotation: AbstractPointAnnotation

    def neuroglancer_precompute_args(self, output_prefix: str, metadata: dict[str, Any]) -> dict[str, Any]:
        return {}

    def neuroglancer_precompute(self, output_prefix: str, voxel_spacing: float) -> None:
        fs = self.config.fs
        annotation_path = self.annotation.get_output_path()
        precompute_path = self._get_neuroglancer_precompute_path(annotation_path, output_prefix)
        metadata = self.annotation.metadata
        tmp_path = fs.localwritable(precompute_path)
        points.encode_annotation(
            self.annotation.get_output_data(annotation_path),
            metadata,
            Path(tmp_path),
            voxel_spacing * 1e-10,
            **self.neuroglancer_precompute_args(annotation_path, metadata),
        )
        fs.push(tmp_path)


class OrientedPointAnnotationPrecompute(PointAnnotationPrecompute):
    def neuroglancer_precompute_args(self, output_prefix: str, metadata: dict[str, Any]) -> dict[str, Any]:
        return {"is_oriented": True}


class InstanceSegmentationAnnotationPrecompute(PointAnnotationPrecompute):
    annotation: InstanceSegmentationAnnotation

    def neuroglancer_precompute_args(self, output_prefix: str, metadata: dict[str, Any]) -> dict[str, Any]:
        instance_ids = self.annotation.get_distinct_ids(output_prefix)

        annotation_hash_input = colors.to_base_hash_input(metadata)
        color_seed = colors.generate_hash({**annotation_hash_input, **{"shape": "InstanceSegmentation"}})
        color_values, _ = colors.get_int_colors(len(instance_ids), exclude=[], seed=color_seed)
        color_map = dict(zip(instance_ids, color_values))
        object_name = metadata.get("annotation_object", {}).get("name", "")
        names_by_id = {instance_id: f"{object_name} {instance_id}" for instance_id in instance_ids}
        return {
            "names_by_id": names_by_id,
            "label_key_mapper": lambda x: x["instance_id"],
            "color_mapper": lambda x: color_map.get(x["instance_id"], (255, 255, 255)),
        }


class SegmentationMaskAnnotationPrecompute(BaseAnnotationPrecompute):
    annotation: VolumeAnnotationSource

    def _get_shape(self) -> str:
        return "SegmentationMask"

    def neuroglancer_precompute(self, output_prefix: str, voxel_spacing: float) -> None:
        fs = self.config.fs
        annotation_path = self.annotation.get_output_path()
        precompute_path = self._get_neuroglancer_precompute_path(annotation_path, output_prefix)
        tmp_path = fs.localwritable(precompute_path)
        zarr_file_path = fs.destformat(self.annotation.get_output_filename(annotation_path, "zarr"))
        segmentation_mask.encode_segmentation(
            zarr_file_path,
            Path(tmp_path),
            resolution=(voxel_spacing,) * 3,
            delete_existing=True,
            include_mesh=True,
        )
        fs.push(tmp_path)
